from locust import HttpUser, task, between, events

total_requests = 0
locust_env = None
MAX_REQUESTS = 100000  # 100k requests limit
test_stopped = False

@events.init.add_listener
def on_locust_init(environment, **kwargs):
    global locust_env
    locust_env = environment

@events.request.add_listener
def on_request(request_type, name, response_time, response_length, response, context, exception, start_time, url, **kwargs):
    global total_requests, locust_env, test_stopped
    
    if test_stopped:
        return

    total_requests += 1
    status_code = getattr(response, "status_code", None)

    # Condition 1: Agar website down ho jaye
    if exception or status_code != 200:
        test_stopped = True
        print("\n" + "🔥" * 30)
        print("🚨 WEBSITE DOWN DETECTED! 🚨")
        print(f"❌ Exact request kis par down hui: {total_requests}")
        print(f"⚠️ Error / Status Code        : {exception if exception else f'HTTP {status_code}'}")
        print("🔥" * 30 + "\n")
        
        if locust_env and locust_env.runner:
            locust_env.runner.quit()
            
    # Condition 2: Agar 100k requests successfully poori ho jayein
    elif total_requests >= MAX_REQUESTS:
        test_stopped = True
        print("\n" + "✅" * 30)
        print(f"🏆 SUCCESS: Website is very strong!")
        print(f"🎯 Total {MAX_REQUESTS} requests bina kisi error ke successfully process ho gayi.")
        print("✅" * 30 + "\n")
        
        if locust_env and locust_env.runner:
            locust_env.runner.quit()

class WebAppUser(HttpUser):
    wait_time = between(0.1, 0.5)

    @task
    def load_homepage(self):
        if not test_stopped:
            with self.client.get("/", catch_response=True, timeout=10) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"Failed with status: {response.status_code}")
