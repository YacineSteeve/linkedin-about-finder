import pickle
from pathlib import Path
from typing import Dict, Literal, Tuple

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


Person_Type = Dict[Literal["first_name", "last_name"], str]
SearchResult_Type = Tuple[Person_Type, bool, str, str, bool, str]


def set_cookies(driver: webdriver.Firefox) -> None:
    cookies_file_path: Path = Path("cookies.pkl")

    if not cookies_file_path.exists():
        raise FileNotFoundError("Cookies file not found. Please login to LinkedIn and save the cookies to cookies.pkl")

    for cookie in pickle.load(open("cookies.pkl", "rb")):
        driver.add_cookie(cookie)


def get_xpath(element: str, value: str) -> str:
    return f"//{element}[@data-tracking-control-name='{value}']"


def find_element(driver: webdriver.Firefox, element: str, value: str):
    try:
        return driver.find_element(By.XPATH, get_xpath(element, value))
    except NoSuchElementException:
        return None


def find_elements(driver: webdriver.Firefox, element: str, value: str):
    try:
        return driver.find_elements(By.XPATH, get_xpath(element, value))
    except NoSuchElementException:
        return None


def get_about(person: Person_Type) -> SearchResult_Type:
    linkedin: str = "https://www.linkedin.com"

    options: webdriver.FirefoxOptions = webdriver.FirefoxOptions()
    options.add_argument("--private")

    driver: webdriver.Firefox = webdriver.Firefox(options=options)
    driver.implicitly_wait(3)

    about_found: bool = False
    persons_about: str = ""
    profile_link: str = ""
    error_occurred: bool = False
    error_message: str = ""

    try:
        driver.get(linkedin)

        set_cookies(driver)

        logo = find_element(driver, "a", "seo-authwall-base_nav-header-logo")

        while logo:
            logo.click()
            logo = find_element(driver, "a", "seo-authwall-base_nav-header-logo")

        current_url = driver.current_url

        people_search_button = find_element(driver, "a", "guest_homepage-basic_guest_nav_menu_people")

        while not people_search_button:
            driver.get(current_url)
            people_search_button = find_element(driver, "a", "guest_homepage-basic_guest_nav_menu_people")

        people_search_button.click()

        first_name_input = find_element(
            driver,
            "input",
            "people-guest_people-search-bar_first-name_dismissable-input"
        )
        last_name_input = find_element(
            driver,
            "input",

            "people-guest_people-search-bar_last-name_dismissable-input"
        )
        search_button = find_element(
            driver,
            "button",
            "people-guest_people-search-bar_base-search-bar-search-submit"
        )

        first_name_input.clear()
        first_name_input.send_keys(person["first_name"])
        last_name_input.clear()
        last_name_input.send_keys(person["last_name"])

        search_button.click()

        results_list_elements = find_elements(
            driver,
            "a",
            "people-guest_people_search-card"
        )

        if results_list_elements:
            results_list_elements[1].click()

        signin_prompt_close_button = find_element(
            driver,
            "button",
            "public_profile_contextual-sign-in-modal_modal_dismiss"
        )

        if signin_prompt_close_button:
            signin_prompt_close_button.click()

        try:
            about = driver.find_element(By.XPATH, "//section[@data-section='summary']/div/p")

            persons_about = about.text
            about_found = True
            profile_link = driver.current_url

        except NoSuchElementException:
            pass

    except Exception as e:
        error_occurred = True
        error_message = str(e)

    finally:
        driver.quit()

    return person, about_found, persons_about, profile_link, error_occurred, error_message


if __name__ == "__main__":
    """
    This script will search for a person on LinkedIn and return their about text
    """

    print(
        "\n" + "=" * 50 +
        "\n\033[0;35m" +
        "LinkedIn About Search".center(50) +
        "\033[0m\n" +
        "=" * 50 + "\n"
    )

    person_to_search: Person_Type = {
        "first_name": input("Enter the first name: "),
        "last_name": input("Enter the last name: ")
    }
    person_to_search_str = f"{person_to_search['first_name']} {person_to_search['last_name']}"

    print("\n\033[0;36mSearching...\033[0m\n")

    _, found, about_text, url, error, _, = get_about(person_to_search)

    if error:
        print(
            f"\033[0;31mAn error occurred while searching for \"{person_to_search_str}\"." +
            "\nPlease try again later.\033[0m"
        )
    else:
        print(
            "-" * 50 + "\n" +
            f"\nAbout \033[0;32m{person_to_search_str}\033[0m :\n" +
            f"\n{about_text if found else 'No information found'}\n" +
            "\n" + "-" * 50
        )

        if found:
            print(f"\nSee more at \033[0;34m{url}\033[0m\n")
