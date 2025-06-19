import os
import json
import time
from kafka import KafkaProducer
from sqlalchemy import create_engine, text

print("Outbox Poller is starting...")
time.sleep(15) # 다른 서비스들이 시작될 시간을 줍니다.

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
MARIADB_URL = os.getenv("MARIADB_URL")

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    acks='all',  # <--- 이 설정 추가: 리더와 모든 팔로워에 메시지가 복제될 때까지 대기
    # Kafka 연결 재시도 설정
    reconnect_backoff_ms=1000,
    reconnect_backoff_max_ms=10000,
    retries=5
)

engine = create_engine(MARIADB_URL)

print("Outbox Poller connected to Kafka and DB. Start polling...")

while True:
    try:
        with engine.connect() as connection:
            # 처리되지 않은('new') 이벤트를 트랜잭션과 함께 조회
            with connection.begin(): 
                query = text("SELECT event_id, topic, payload FROM outbox WHERE status = 'new' ORDER BY event_id ASC LIMIT 10 FOR UPDATE")
                result = connection.execute(query)
                events = result.fetchall()

            if not events:
                time.sleep(1) # 새 이벤트가 없으면 5초 대기
                continue
            
            print(f"Found {len(events)} new events in outbox.")
            
            for event in events:
                event_id, topic, payload = event
                # Kafka로 이벤트 전송
                future = producer.send(topic, value=payload)
                # 전송 성공 확인 (선택적이지만 안정성을 높임)
                future.get(timeout=10)
                print(f"Sent event {event_id} to Kafka topic '{topic}'")

                # 처리 완료 상태로 업데이트
                with connection.begin():
                    update_query = text("UPDATE outbox SET status = 'processed' WHERE event_id = :event_id")
                    connection.execute(update_query, {"event_id": event_id})
            
            producer.flush()
    except Exception as e:
        print(f"An error occurred in Outbox Poller: {e}")
        time.sleep(10) # 에러 발생 시 잠시 대기 후 재시도