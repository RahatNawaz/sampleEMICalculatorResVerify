import os
import subprocess
from appium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

test_data_dictionary = {"loan": [100000, 325000, 450000, 99000000, 50000],
                        "interest": [9.0, 9.5, 11.0, 10.0, 12.0],
                        "period": [2, 5, 7, 4, 9],
                        "pFee": [2.0, 1.5, 1.8, 1.25, 2.2],
                        "mEmi": [4568, 6826, 7705, 2510896, 759],
                        "tinterest": [9643, 84536, 197228, 21522996, 31995],
                        "tpFee": [2000, 4875, 8100, 1237500, 1100],
                        "tPayment": [109643, 409536, 647228, 120522996, 81995]}

result_file = open("Results.txt", "w+")


def tear_down():
    driver.quit()


def get_device_info():
    connected_devices = os.popen('adb devices').read().strip().split('\n')[1:]

    for deviceId in connected_devices:
        # get device name
        device_udid = deviceId.split('\t')[0]

        command_for_version = "adb -s {} shell getprop ro.build.version.release".format(device_udid)
        device_version = subprocess.Popen(command_for_version, shell=True)

        return device_udid, device_version


def create_driver_for_device(platform_id, platform_version):
    print("Starting appium server")
    command = "appium -p 4327"
    subprocess.Popen(command, shell=True)

    print("Creating Driver")
    caps = {}
    caps["platformName"] = "Android"
    caps["appium:platformVersion"] = "{}".format(platform_version)
    caps["appium:udid"] = platform_id
    caps["appium:automationName"] = "UiAutomator2"
    caps["appium:app"] = "app/emi-calculator.apk"
    caps["appium:ensureWebviewsHavePages"] = True
    caps["appium:nativeWebScreenshot"] = True
    caps["appium:newCommandTimeout"] = 3600
    caps["appium:connectHardwareKeyboard"] = True
    caps["appium:ignoreHiddenApiPolicyError"] = True

    appium_server_to_connect_with = "http://127.0.0.1:4327/wd/hub"

    driver_created = webdriver.Remote(appium_server_to_connect_with, caps)
    return driver_created


def convert_element_text_to_round_int(element_text):
    value_converted_to_round_int = round(float(element_text.replace(",", '')))
    return value_converted_to_round_int


def send_test_data_and_check_result():
    WebDriverWait(driver, 10). \
        until(expected_conditions.presence_of_element_located((By.XPATH, "//android.widget.TextView[@text="
                                                                         "'EMI Calculator']")))
    emi_calculator_button = driver.find_element(by=By.XPATH, value="/hierarchy/android.widget.FrameLayout/"
                                                                   "android.widget.LinearLayout/"
                                                                   "android.widget.FrameLayout/"
                                                                   "android.widget.LinearLayout/"
                                                                   "android.widget.FrameLayout/"
                                                                   "android.widget.RelativeLayout/"
                                                                   "android.widget.LinearLayout/"
                                                                   "android.widget.RelativeLayout[2]/"
                                                                   "android.widget.FrameLayout[1]/"
                                                                   "android.widget.LinearLayout/"
                                                                   "android.widget.ImageView")
    emi_calculator_button.click()

    WebDriverWait(driver, 10). \
        until(expected_conditions.presence_of_element_located((By.XPATH, "//android.widget.TextView[@text="
                                                                         "'Calculator']")))

    amount_input_field = driver.find_element(by=By.ID, value="com.continuum.emi.calculator:id/etLoanAmount")
    interest_input_field = driver.find_element(by=By.ID, value="com.continuum.emi.calculator:id/etInterest")
    years_input_field = driver.find_element(by=By.ID, value="com.continuum.emi.calculator:id/etYears")
    processing_fee_input_field = driver.find_element(by=By.ID, value="com.continuum.emi.calculator:id/etFee")
    calculate_button = driver.find_element(by=By.ID, value="com.continuum.emi.calculator:id/btnCalculate")

    for index in range(len(test_data_dictionary["loan"])):
        amount_input_field.clear()
        amount_input_field.send_keys("{}".format(test_data_dictionary["loan"][index]))

        interest_input_field.clear()
        interest_input_field.send_keys("{}".format(test_data_dictionary["interest"][index]))

        years_input_field.clear()
        years_input_field.send_keys("{}".format(test_data_dictionary["period"][index]))

        processing_fee_input_field.clear()
        processing_fee_input_field.send_keys("{}".format(test_data_dictionary["pFee"][index]))

        calculate_button.click()

        monthly_emi_result = driver.find_element(by=By.ID, value="com.continuum.emi.calculator:id/monthly_emi_result")
        total_interest_result = driver.find_element(by=By.ID,
                                                    value="com.continuum.emi.calculator:id/total_interest_result")
        processing_fee_result = driver.find_element(by=By.ID,
                                                    value="com.continuum.emi.calculator:id/processing_fee_result")
        total_payment_result = driver.find_element(by=By.ID,
                                                   value="com.continuum.emi.calculator:id/total_payment_result")

        monthly_emi = convert_element_text_to_round_int(monthly_emi_result.text)
        total_interest = convert_element_text_to_round_int(total_interest_result.text)
        processing_fee = convert_element_text_to_round_int(processing_fee_result.text)
        total_payment = convert_element_text_to_round_int(total_payment_result.text)
        test_case_fail = "false"

        if monthly_emi != test_data_dictionary["mEmi"][index]:
            if test_case_fail == "false":
                test_case_fail = "true"
                result_file.write("# Results missmatch found for test data list %d\r\n" % (index + 1))
            result_file.write("\tExpected mEmi: %d\tFound mEmi: %d\r\n" % (test_data_dictionary["mEmi"][index], monthly_emi))

        if total_interest != test_data_dictionary["tinterest"][index]:
            if test_case_fail == "false":
                test_case_fail = "true"
                result_file.write("# Results missmatch found for test data list %d\r\n" % (index + 1))
            result_file.write("\tExpected tinterest: %d\tFound tinterest: %d\r\n" % (test_data_dictionary
                                                                                     ["tinterest"][index],
                                                                                     total_interest))

        if processing_fee != test_data_dictionary["tpFee"][index]:
            if test_case_fail == "false":
                test_case_fail = "true"
                result_file.write("# Results missmatch found for test data list %d\r\n" % (index + 1))
            result_file.write("\tExpected tpFee: %d\tFound tpFee: %d\r\n" % (test_data_dictionary["tpFee"][index],
                                                                             processing_fee))

        if total_payment != test_data_dictionary["tPayment"][index]:
            if test_case_fail == "false":
                test_case_fail = "true"
                result_file.write("# Results missmatch found for test data list %d\r\n" % (index + 1))
            result_file.write("\tExpected tPayment: %d\tFound tPayment: %d\r\n" % (test_data_dictionary
                                                                                   ["tPayment"][index], total_payment))

        if test_case_fail == "false":
            result_file.write("# Results are correct for test data %d\r\n" % (index+1))


android_id, android_version = get_device_info()
driver = create_driver_for_device(android_id, android_version)
send_test_data_and_check_result()
result_file.close()
tear_down()

