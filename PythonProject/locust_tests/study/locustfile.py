from locust import HttpUser, task, between, SequentialTaskSet, TaskSet, events
from config.settings import BASE_URL, TENANT
from utils.logger import setup_logger

logger = setup_logger()


class MemberBehavior(TaskSet):
    
    def on_start(self):
        self.client.headers.update({"Content-Type": "application/json", "x-tenant": TENANT})
        self.member_id = "123456"
        logger.info(f"User started")

    def on_stop(self):
        logger.info(f"User stopped")

    @task(3)
    def get_member_profile(self):
        response = self.client.get("/api/v1/wx-mini/member/profile")
        try:
            response_json = response.json()
            if response_json and isinstance(response_json, dict):
                self.member_id = response_json.get("data", {}).get("memberId", "123456")
        except Exception:
            pass

    @task(2)
    def update_member_info(self):
        self.client.post(
            "/api/v1/wx-mini/member/update",
            json={"memberId": self.member_id, "memberName": "LocustTestUser"}
        )


class MarketingBehavior(TaskSet):

    def on_start(self):
        self.client.headers.update({"Content-Type": "application/json", "x-tenant": TENANT})

    @task(2)
    def submit_questionnaire(self):
        self.client.post(
            "/api/v1/wx-mini/marketing/questionnaire/submit",
            json={
                "questionnaireId": 582,
                "memberId": "123456",
                "itemList": [{"questionId": 1, "scoreValue": 3}]
            }
        )

    @task(1)
    def get_coupon_list(self):
        self.client.get("/api/v1/wx-mini/marketing/coupon/list")


class MixedBehavior(SequentialTaskSet):

    @task
    class MemberTasks(TaskSet):
        @task(2)
        def get_profile(self):
            self.client.get("/api/v1/wx-mini/member/profile")

        @task(1)
        def update_profile(self):
            self.client.post(
                "/api/v1/wx-mini/member/update",
                json={"memberId": "123456", "memberName": "SequentialUser"}
            )

        @task
        def stop(self):
            self.interrupt()

    @task
    class MarketingTasks(TaskSet):
        @task(3)
        def submit_survey(self):
            self.client.post(
                "/api/v1/wx-mini/marketing/questionnaire/submit",
                json={
                    "questionnaireId": 582,
                    "memberId": "123456",
                    "itemList": [{"questionId": 1, "scoreValue": 3}]
                }
            )

        @task
        def stop(self):
            self.interrupt()


class MemberUser(HttpUser):
    host = BASE_URL
    tasks = [MemberBehavior]
    wait_time = between(1, 3)


class MarketingUser(HttpUser):
    host = BASE_URL
    tasks = [MarketingBehavior]
    wait_time = between(2, 5)


class MixedUser(HttpUser):
    host = BASE_URL
    tasks = [MixedBehavior]
    wait_time = between(1, 4)


@events.request.add_listener
def request_handler(request_type, name, response_time, response_length, exception, context, **kwargs):
    if exception:
        logger.error(f"FAILURE {request_type} {name} {response_time:.2f}ms {str(exception)}")
    else:
        logger.info(f"SUCCESS {request_type} {name} {response_time:.2f}ms {response_length} bytes")


@events.quitting.add_listener
def quitting_handler(environment, **kwargs):
    stats = environment.stats.total
    logger.info("=== Test Summary ===")
    logger.info(f"Total requests: {stats.request_count}")
    logger.info(f"Total failures: {stats.failure_count}")
    logger.info(f"Requests/s: {stats.avg_rps}")
    logger.info(f"Median response time: {stats.median_response_time}ms")
    logger.info(f"95th percentile: {stats.get_response_time_percentile(0.95)}ms")