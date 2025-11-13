import asyncio
import json
import logging
from pathlib import Path

import httpx

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s][%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# 설정
VIRTUAL_SERVER_BASE_URL = "http://localhost:8005"
TASK_WAS_BASE_URL = "http://localhost:8001"
USER_ID = "test_user"
BOT_ID = "test_bot"
BOT_RESPONSE_WAIT_TIME = 3.0  # 봇 응답 후 대기 시간 (초)
TEST_MESSAGES_FILE = "test_messages.json"  # 테스트 메시지 JSON 파일
CONCURRENT_USERS = 1  # 동시 테스트할 사용자 수


def load_test_messages(file_path: str = TEST_MESSAGES_FILE) -> list[dict]:
    """JSON 파일에서 테스트 메시지 로드"""
    # 현재 파일의 디렉토리 기준으로 경로 설정
    current_dir = Path(__file__).parent
    json_path = current_dir / file_path

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            messages = json.load(f)
        logger.info(f"📂 테스트 메시지 로드 완료: {json_path}")
        logger.info(f"📊 로드된 메시지 수: {len(messages)}")
        return messages
    except FileNotFoundError:
        logger.error(f"❌ 파일을 찾을 수 없습니다: {json_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON 파싱 오류: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ 파일 로드 중 오류: {e}")
        raise


async def send_simulate_message(
    user_id: str, bot_id: str, text: str, postback: str | None = None
):
    """simulate-message API 호출"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            payload = {"bot_id": bot_id, "user_id": user_id, "text": text}
            if postback:
                payload["postback"] = postback
                logger.info(
                    f"[{user_id}] 🚀 메시지 전송: text='{text}', postback={postback}"
                )
            else:
                logger.info(f"[{user_id}] 🚀 메시지 전송: text='{text}'")

            response = await client.post(
                f"{VIRTUAL_SERVER_BASE_URL}/simulate-message",
                json=payload,
            )

            response.raise_for_status()
            logger.info(
                f"[{user_id}] ✅ 메시지 전송 완료: status={response.status_code}"
            )
            return True

        except Exception as e:
            logger.error(f"[{user_id}] ❌ 메시지 전송 실패: {e}")
            return False


async def wait_for_bot_response(user_id: str):
    """봇 응답을 대기합니다. task-was의 status API를 폴링하여 응답 완료를 확인합니다."""
    async with httpx.AsyncClient(timeout=600.0) as client:
        stable_count = 0

        logger.info(f"[{user_id}] ⏳ 봇 응답 대기 중...")

        while True:
            try:
                response = await client.get(
                    f"{TASK_WAS_BASE_URL}/api/v1/tasks/status/{user_id}"
                )
                response.raise_for_status()
                data = response.json()

                current_status = data.get("status")

                if current_status == "processing":
                    # 아직 처리 중
                    logger.info(f"[{user_id}] 🔄 봇 응답 작업을 처리중입니다....")
                    stable_count = 0
                    await asyncio.sleep(0.5)
                    continue
                elif current_status == "ready":
                    # 봇 응답 작업이 준비 상태 (곧 응답할 것)
                    logger.info(f"[{user_id}] 🔄 봇 응답 작업이 준비 상태입니다....")
                    stable_count = 0
                    await asyncio.sleep(0.5)
                    continue
                else:
                    # 봇 응답 작업을 하지 않고 있음. 이후 3초간 안정적일 경우 응답 완료로 간주
                    stable_count += 1

                    # 3초 동안 안정적이면 완료
                    if stable_count >= int(BOT_RESPONSE_WAIT_TIME / 0.5):
                        logger.info(f"[{user_id}] ✅ 봇 응답 완료 (3초 안정)")
                        return True

                await asyncio.sleep(0.5)

            except Exception as e:
                logger.error(f"[{user_id}] ❌ 봇 응답 확인 중 오류: {e}")
                await asyncio.sleep(1)


async def test_main(user_id: str, bot_id: str):
    """메인 테스트 함수"""
    # JSON 파일에서 테스트 메시지 로드
    try:
        test_messages = load_test_messages()
    except Exception as e:
        logger.error(f"테스트 메시지 로드 실패: {e}")
        return

    logger.info("=" * 80)
    logger.info("🤖 Virtual Bot Server 테스트 시작")
    logger.info(f"📍 서버 URL: {VIRTUAL_SERVER_BASE_URL}")
    logger.info(f"👤 사용자 ID: {user_id}")
    logger.info(f"🤖 봇 ID: {bot_id}")
    logger.info(f"📝 테스트 메시지 수: {len(test_messages)}")
    logger.info("=" * 80)

    for idx, msg in enumerate(test_messages, 1):
        logger.info(f"\n[{user_id}] [{idx}/{len(test_messages)}] 메시지 처리 시작")

        # 메시지 전송
        if msg.get("postback"):
            success = await send_simulate_message(
                user_id=user_id,
                bot_id=bot_id,
                text=msg["text"],
                postback=msg["postback"],
            )
        else:
            success = await send_simulate_message(
                user_id=user_id, bot_id=bot_id, text=msg["text"]
            )

        if not success:
            logger.error(f"[{user_id}] 메시지 전송 실패, 테스트 중단")
            break

        # 봇 응답 대기
        await wait_for_bot_response(user_id=user_id)
        if idx < len(test_messages):
            logger.info(f"[{user_id}] 다음 메시지 준비...\n")
        else:
            logger.info(f"[{user_id}] 마지막 메시지 전송 완료\n")

    logger.info("=" * 80)
    logger.info(f"[{user_id}] ✅ 모든 테스트 메시지 전송 완료")
    logger.info("=" * 80)


async def main():
    try:
        tasks = [
            test_main(f"{USER_ID}_{i + 1}", BOT_ID) for i in range(CONCURRENT_USERS)
        ]

        await asyncio.gather(*tasks)
    except Exception as e:
        logger.error(f"테스트 실행 중 오류 발생: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n⚠️  테스트 중단됨")
