# import pytest 
# import allure 
# from pathlib import Path 
# from playwright.sync_api import sync_playwright 
# # ======================================================================== 
# # PYTEST + PLAYWRIGHT TEST CONFIGURATION FILE 
# # ======================================================================== 
# # This file provides: 
# # 1. Command-line options (browser, base URL, video, screenshots, etc.) 
# # 2. Hooks to track test results 
# # 3. Fixtures for browser setup and teardown 
# # 4. Screenshot, video, and trace attachments to Allure reports
# # 5. PAGE CREATION AND TEST ARTIFACT MANAGEMENT
# # ======================================================================== 



# # ---------------------------------------------------------------------------- 
# # STEP 1: ADD COMMAND LINE OPTIONS              - If we don't give any command line then will
# #                                               take them from pytest.ini default                               
# # ---------------------------------------------------------------------------- 
# def pytest_addoption(parser): 
#     """ Adds command line options for test configuration. 
#     You can override these when running pytest or store defaults in pytest.ini. """ 
#     parser.addoption("--browser", default="chromium", help="Browser: chromium, firefox, webkit") 
#     parser.addoption("--headed", action="store_true", help="Run in headed (visible) mode") 
#     #parser.addoption("--base-url", default="http://localhost/opencart/upload/", help="Base URL for tests") 
#     parser.addoption("--video", default="retain-on-failure", help="Record video: on, off, retain-on-failure") 
#     parser.addoption("--screenshot", default="only-on-failure", help="Take screenshot: on, off, only-on-failure") 
#     parser.addoption("--tracing", default="retain-on-failure", help="Tracing: on, off, retain-on-failure")






# # ---------------------------------------------------------------------------- 
# # STEP 2: GET CONFIGURATION VALUE (CMDLINE OR pytest.ini)           - will read options from function above pytest_addoption(parser)
# #                                                      or will read option from command line
# # ---------------------------------------------------------------------------- 
# def get_config_value(config, option_name): 
#     """ Helper to read configuration values. Tries to get from command line first, 
#     otherwise from pytest.ini. Supports both string and boolean options. """ 
#     # Try command-line first 
#     cmd_value = config.getoption(option_name)
#     if cmd_value is not None: 
#         return cmd_value 
    
#     # Fallback to pytest.ini 
#     if option_name == "headed": 
#         ini_value = config.getini(option_name) 
#         return ini_value.lower() == "true" if isinstance(ini_value, str) else ini_value
#     else: 
#         return config.getini(option_name)
    


# # ---------------------------------------------------------------------------- 
# # STEP 3: HOOK TO TRACK TEST RESULTS (PASS/FAIL) 
# # ---------------------------------------------------------------------------- 
# @pytest.hookimpl(hookwrapper=True)             # - hookimpl: name of the hook, 
# def pytest_runtest_makereport(item, call):     # function will capture the result of the test
#     """ Captures the test result (pass/fail/skip) after each test.
#     This is used later to decide whether to take screenshots or save traces. """
#     outcome = yield
#     report = outcome.get_result()
#     setattr(item, f"rep_{report.when}", report)



# # ---------------------------------------------------------------------------- 
# # STEP 4: FIXTURE 1 - BROWSER CONTEXT SETUP 
# # ---------------------------------------------------------------------------- 
# @pytest.fixture(scope="function")
# def browser_context(request): 
#     """ Creates and manages the Playwright browser context. 
#     - Reads configuration (browser, headed mode, video settings) 
#     - Starts the Playwright browser - Enables video recording if configured 
#     - Cleans up automatically after each test """ 
    
#     # Read configuration values 
#     browser_name = get_config_value(request.config, "browser")      # read the options 
#     headed_flag = get_config_value(request.config, "headed")        # from function 1
#     video_option = get_config_value(request.config, "video")        # pytest_addoption(parser)
#     print(f"🎯 Starting browser: {browser_name}")
#     print(f"🎯 Headless mode: {not headed_flag} (headed={headed_flag})") 
    
#     # Start Playwright 
#     playwright = sync_playwright().start() 
    
#     # Launch the specified browser
#     if browser_name.lower() == "chromium": 
#         browser = playwright.chromium.launch(headless=not headed_flag)  # not headed_flag is oposite from
#     elif browser_name.lower() == "firefox":                         # pytest.ini ---headed - True
#         browser = playwright.firefox.launch(headless=not headed_flag)   # so headed_flag is True, --headed
#     elif browser_name.lower() == "webkit":
#         browser = playwright.webkit.launch(headless=not headed_flag) 
#     else:
#         raise ValueError(f"❌ Unsupported browser: {browser_name}")

#     # After creating Browser we create context
#     # Create a browser context (optionally with video recording) 
#     if video_option in ["on", "retain-on-failure"]:
#         context = browser.new_context(record_video_dir="reports/videos")
#     else: 
#         context = browser.new_context() 
        
#     # Yield the context for use in tests 
#     yield context 
    
#     # Clean up after the test
#     print("🧹 Closing browser context and stopping Playwright...")
#     context.close()
#     browser.close()
#     playwright.stop()



# # ----------------------------------------------------------------------------
# # STEP 5: FIXTURE 2 - PAGE CREATION AND TEST ARTIFACT MANAGEMENT    # create page after browser
# # ----------------------------------------------------------------------------
# @pytest.fixture(scope="function")
# def page(request, browser_context):
#     """ Creates a new browser page for each test.
#     - Navigates to the base URL - Starts tracing (if enabled)
#     - Captures screenshots, traces, and videos for failed tests
#     - Attaches all artifacts to Allure report """
    
#     # Read test configuration
#     base_url = get_config_value(request.config, "base_url")             # read this from function 1
#     screenshot_option = get_config_value(request.config, "screenshot")  # pytest_addoption(parser)
#     tracing_option = get_config_value(request.config, "tracing")
#     video_option = get_config_value(request.config, "video")
    
#     print(f"🌐 Navigating to: {base_url}")
    
#     # Start tracing if enabled 
#     if tracing_option in ["on", "retain-on-failure"]:
#         print("📹 Tracing enabled - capturing screenshots and actions")
#         browser_context.tracing.start(screenshots=True, snapshots=True, sources=True)
        
#     # Create and navigate to base URL
#     page = browser_context.new_page()
#     page.goto(base_url)
    
#     # Yield the page to the test
#     yield page

#     # ------------------------------------------------------------------------
#     # After the test: manage artifacts (screenshots, videos, traces)
#     # ------------------------------------------------------------------------
#     test_name = request.node.name
#     test_failed = hasattr(request.node, "rep_call") and request.node.rep_call.failed
    
#     print(f"📊 Test '{test_name}' result: {'❌ FAILED' if test_failed else '✅ PASSED'}")
    
#     # Save and attach trace
#     if tracing_option in ["on", "retain-on-failure"]:
#         trace_path = f"reports/traces/{test_name}_trace.zip"
#         browser_context.tracing.stop(path=trace_path)
#         print(f"💾 Trace saved: {trace_path}")

#         # Attach trace to Allure report if test failed
#         # Currently ZIP file is not supporting to attach in allure reports
#         # if test_failed: # allure.attach.file( # trace_path,
#         # name=f"{test_name}_trace",
#         # attachment_type=allure.attachment_type.ZIP # )
#         # print("📎 Trace attached to Allure report")


#     # Take screenshot if test failed
#     if test_failed and screenshot_option in ["on", "only-on-failure"]:
#         screenshot_path = f"reports/screenshots/{test_name}.png"
#         page.screenshot(path=screenshot_path)
#         print(f"📸 Screenshot saved: {screenshot_path}")
        
#         # Attach to Allure report
#         allure.attach.file( screenshot_path, name=f"{test_name}_screenshot", attachment_type=allure.attachment_type.PNG )
        
#         print("📎 Screenshot attached to Allure report")
        
#     # Attach video if available and test failed
#     if test_failed and video_option in ["on", "retain-on-failure"]:
#         video_path = page.video.path() if page.video else None
#         if video_path and Path(video_path).exists():
#             allure.attach.file( video_path, name=f"{test_name}_video", attachment_type=allure.attachment_type.WEBM )
#             print("🎥 Video attached to Allure report")
    







import pytest
import allure
from pathlib import Path
from playwright.sync_api import sync_playwright


# ----------------------------------------------------------------------------
# STEP 1: ADD CUSTOM OPTIONS (DOAR CE NU EXISTĂ ÎN PLUGINURI)
# ----------------------------------------------------------------------------
def pytest_addoption(parser):
    parser.addoption("--based-url", default="http://localhost/opencart/upload")
    parser.addoption("--browser-name", default="chromium")   # 🔥 redenumit (NU --browser)
    parser.addoption("--headed", action="store_true")
    parser.addoption("--video-mode", default="retain-on-failure")
    parser.addoption("--screenshot-mode", default="only-on-failure")
    parser.addoption("--trace-mode", default="retain-on-failure")


# ----------------------------------------------------------------------------
# STEP 2: CONFIG HELPER
# ----------------------------------------------------------------------------
def get_option(config, name):
    return config.getoption(name)


# ----------------------------------------------------------------------------
# STEP 3: TEST RESULT HOOK
# ----------------------------------------------------------------------------
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


# ----------------------------------------------------------------------------
# STEP 4: BROWSER FIXTURE
# ----------------------------------------------------------------------------
@pytest.fixture(scope="function")
def browser_context(request):
    browser_name = get_option(request.config, "browser_name")
    headed = get_option(request.config, "headed")
    video_mode = get_option(request.config, "video_mode")

    print(f"\n🚀 Browser: {browser_name} | Headed: {headed}")

    playwright = sync_playwright().start()

    if browser_name == "chromium":
        browser = playwright.chromium.launch(headless=not headed)
    elif browser_name == "firefox":
        browser = playwright.firefox.launch(headless=not headed)
    elif browser_name == "webkit":
        browser = playwright.webkit.launch(headless=not headed)
    else:
        raise ValueError(f"Invalid browser: {browser_name}")

    context = browser.new_context(
        record_video_dir="reports/videos"
        if video_mode in ["on", "retain-on-failure"]
        else None
    )

    yield context

    context.close()
    browser.close()
    playwright.stop()


# ----------------------------------------------------------------------------
# STEP 5: PAGE FIXTURE
# ----------------------------------------------------------------------------
@pytest.fixture(scope="function")
def page(request, browser_context):
    base_url = get_option(request.config, "base_url")
    screenshot_mode = get_option(request.config, "screenshot_mode")
    trace_mode = get_option(request.config, "trace_mode")
    video_mode = get_option(request.config, "video_mode")

    page = browser_context.new_page()

    # Start tracing
    if trace_mode in ["on", "retain-on-failure"]:
        browser_context.tracing.start(screenshots=True, snapshots=True)

    print(f"🌐 Opening: {base_url}")
    page.goto(base_url)

    yield page

    test_name = request.node.name
    failed = hasattr(request.node, "rep_call") and request.node.rep_call.failed

    # TRACE
    if trace_mode in ["on", "retain-on-failure"]:
        trace_path = f"reports/traces/{test_name}.zip"
        browser_context.tracing.stop(path=trace_path)

    # SCREENSHOT
    if failed and screenshot_mode in ["on", "only-on-failure"]:
        screenshot_path = f"reports/screenshots/{test_name}.png"
        page.screenshot(path=screenshot_path)
        allure.attach.file(
            screenshot_path,
            name="screenshot",
            attachment_type=allure.attachment_type.PNG,
        )

    # VIDEO
    if failed and video_mode in ["on", "retain-on-failure"]:
        if page.video:
            video_path = page.video.path()
            if Path(video_path).exists():
                allure.attach.file(
                    video_path,
                    name="video",
                    attachment_type=allure.attachment_type.WEBM,
                )

## allure generate:     allure generate ./reports/allure-results
## allure visualising: allure serve ./reports/allure-results
## traces visualising: playwright show-trace reports/traces/test_user_registration.zip