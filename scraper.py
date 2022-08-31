# Things to add
# - Limit search results to just weekdays

import json
import requests
import datetime

import html_to_json


def send_post_request(course: str) -> dict:
    """ Send the POST request to the server
    """
    url = "https://api.easi.utoronto.ca/ttb/getPageableCourses"
    payload = {"courseCodeAndTitleProps": {
        "courseCode": "",
        "courseTitle": course + " ",
        "courseSectionCode": "",
        "searchCourseDescription": True},
        "departmentProps": [],
        "campuses": [],
        "sessions": ["20229", "20231", "20229-20231"],
        "requirementProps": [],
        "instructor": "",
        "courseLevels": [],
        "deliveryModes": [],
        "dayPreferences": [],
        "timePreferences": [],
        "divisions": ["ERIN"],
        "creditWeights": [],
        "page": 1,
        "pageSize": 10,
        "direction": "asc"}
    r = requests.post(url, json=payload)
    r_json = html_to_json.convert(r.text)
    return r_json['ttbresponse'][0]['payload'][0]['pageablecourse'][0]['courses'][0]['courses']


def get_timings(course_query: dict, session: str) -> dict:
    course_timing = {}
    for course in course_query:
        if course['sectioncode'][0]['_value'] == session or course['sectioncode'][0]['_value'] == "Y":
            for section in course['sections'][0]['sections']:
                if section['type'][0]['_value'] == "Lecture":
                    for lec in section['meetingtimes'][0]['meetingtimes']:
                        day_raw = lec['start'][0]['day'][0]['_value']
                        start_time_raw = lec['start'][0]['millisofday'][0]['_value']
                        end_time_raw = lec['end'][0]['millisofday'][0]['_value']

                        day = int(day_raw)
                        start_time = str(datetime.timedelta(milliseconds=int(start_time_raw)))
                        end_time = str(datetime.timedelta(milliseconds=int(end_time_raw)))

                        if day not in course_timing:
                            course_timing[day] = []
                        course_timing[day].append((datetime.datetime.strptime(start_time, '%H:%M:%S'),
                                                   datetime.datetime.strptime(end_time, '%H:%M:%S')))

    return course_timing


def get_course_info(main: str, side: list[str], session: str) -> list:
    course_query = send_post_request(main)
    course_timings = [get_timings(course_query, session)]

    side_course_timings = {}
    course_timings.append(side_course_timings)
    for course in side:
        course_query = send_post_request(course)
        timings = get_timings(course_query, session)
        for day in timings:
            if day not in side_course_timings:
                side_course_timings[day] = []
            side_course_timings[day].extend(timings[day])

    return course_timings

