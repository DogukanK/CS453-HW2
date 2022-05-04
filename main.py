#! /usr/bin/env python3

from collections import UserList
from perceval.backends.core.github import GitHub
import argparse
import datetime
import dateutil.parser
import requests
from requests.structures import CaseInsensitiveDict
from itertools import cycle


# create a Git object, pointing to repo_url, using repo_dir for cloning
repo = GitHub(owner='chaoss', repository='metrics', api_token=[YOUR_TOKEN_HERE], sleep_for_rate=True)


total_bug_count = 0
open_bug_count = 0
closed_bug_count = 0
issues_created_last_month = 0
user_list = UserList()
user_count = 0
user_list_with_count = [{'user': '', 'count': 0}]
user_list_with_count_correct = [{'user': '', 'count': 0}]
unassigned_closed_bug_count = 0
res_time_with_no_assignee = 0
res_time_with_assignee = 0
assigned_closed_bug_count = 0
unassigned_bug_count = 0
assigned_bug_count = 0
bugs_last_year = 0
resolved_bugs_last_year = 0
res_time_last_year = 0
created_date = None
first_bug_created_date = None
last_bug_created_date = None
first_bug_flag = False

# Today's date
today_date = datetime.datetime.utcnow().replace(
    tzinfo=datetime.timezone.utc).isoformat()
today_date = dateutil.parser.isoparse(today_date)
print("Today's date is: ", today_date)

for item in repo.fetch(category='issue'):
    if 'pull_request' in item['data']:
        kind = 'Pull request'
    else:
        kind = 'Issue'
        #print(kind , ": " , item['data'])
        total_bug_count += 1
        if item['data']['state'] == 'open':
            open_bug_count += 1
        elif item['data']['state'] == 'closed':
            closed_bug_count += 1
        if first_bug_flag == False:
            first_bug_created_date = item['data']['created_at']
            first_bug_flag = True
        last_bug_created_date = item['data']['created_at']

        if item['data']['assignee'] == None:
            unassigned_bug_count += 1
            if item['data']['state'] == 'closed':
                unassigned_closed_bug_count += 1
                # find average time spent on bug
                if item['data']['closed_at'] != None:
                    res_time_with_no_assignee += (dateutil.parser.isoparse(
                        item['data']['closed_at']) - dateutil.parser.isoparse(item['data']['created_at'])).days

        else:
            assigned_bug_count += 1
            if item['data']['state'] == 'closed':
                # find average time spent on bug
                if item['data']['closed_at'] != None:
                    assigned_closed_bug_count += 1
                    res_time_with_assignee += (dateutil.parser.isoparse(
                        item['data']['closed_at']) - dateutil.parser.isoparse(item['data']['created_at'])).days

        # number of bugs created last month
        created_date = item['data']['created_at']
        created_date = dateutil.parser.isoparse(created_date)
        if (today_date - created_date).days < 30:
            issues_created_last_month += 1

        # number of bugs created last year
        created_date = item['data']['created_at']
        created_date = dateutil.parser.isoparse(created_date)
        if (today_date - created_date).days < 365:
            bugs_last_year += 1
            #print((today_date - created_date).days)
            if item['data']['state'] == 'closed':
                resolved_bugs_last_year += 1
                # calculate resolution time
                created_date = item['data']['created_at']
                created_date = dateutil.parser.isoparse(created_date)
                closed_date = item['data']['closed_at']
                closed_date = dateutil.parser.isoparse(closed_date)
                resolution_time = closed_date - created_date
                res_time_last_year += resolution_time.days

       # List the name of the top 5 users who opened the most number of issues
        if item['data']['user']['login'] not in user_list:
            # print(item['data']['user']['login'])
            user_list.append(item['data']['user']['login'])
            user_count += 1
            # user_list_count.append(1)
            user_list_with_count.append(
                {'user': item['data']['user']['login'], 'count': 1})
            # add number of issues created by each user
        else:
            #user_list_count[user_list.index(item['data']['user']['login'])] += 1
            user_list_with_count[user_list.index(
                item['data']['user']['login'])]['count'] += 1
            # print(user_list_with_count[user_list.index(item['data']['user']['login'])]['count'])


# print(user_list_with_count)

print("----------------Part 2----------------")

# date of first bug
first_bug_created_date = dateutil.parser.parse(first_bug_created_date)
print("Date of first opened issue is: ", first_bug_created_date)

# date of last bug
last_bug_created_date = dateutil.parser.parse(last_bug_created_date)
print("Date of last opened issue is: ", last_bug_created_date)

# repository age
repo_age = last_bug_created_date - first_bug_created_date
print("The repository's age is: ", repo_age.days, " days")

# number of issues created in last month
print("Issues created in the last 30 day is: ", issues_created_last_month)

# number of issues in total
print("It has", total_bug_count, "issues")

# number of contributors
contributors = repo.fetch(category='repository')
headers = CaseInsensitiveDict()
headers["Accept"] = "application/json"
for item in contributors:
    cont = item['data']['contributors_url']
res = requests.get(cont, headers=headers)
# print(len(res.json()))
contributors = len(res.json())
print("It has", contributors, "contributors")

print("----------------Part 3----------------")

# OPEN-CLOSED ISSUES STATUS
print("Open Issue Count", open_bug_count)
print("Closed Issue Count", closed_bug_count)

print("----------------Part 4----------------")

# List the name of the top 5 users who opened the most number of issues
print("Top 5 users who opened the most number of issues")



'''
# There was a problem with the appending of the list, so that's why I corrected it by using the following code,
# it is correcting the data alignment with the new copy of the list, then it is sorting the list and then it is printing the top 5 elements.
# I am not sure if it is the best way to do it, but it works.
'''
#print(user_count)
if user_count < 5:
    print("The number of users is less than 5")
else:
    usercyc = cycle(user_list_with_count)
    for user in user_list_with_count:
        if user['user'] != '':
            uname = user['user']
            nextel = next(usercyc)
            cnt = nextel['count']
            user_list_with_count_correct.append({'user': uname, 'count': cnt})
    #print(user_list_with_count_correct)

    # find the top 5 user who worked on the most number of bugs
    user_list_with_count_correct.sort(key=lambda x: x['count'], reverse=True)
    user_list_with_count_correct = sorted(
        user_list_with_count_correct, key=lambda x: x['count'], reverse=True)

    # print(user_list_with_count)
    #print("user with counts: " , user_list_with_count_correct)

    # print only 5 users
    for i in range(5):
        print(user_list_with_count_correct[i]['user'],
            ": ", user_list_with_count_correct[i]['count'])

print("----------------Part 5----------------")
# number of closed issues with no assignee
print("No of closed issues that did not have any assignee is: ",
      unassigned_closed_bug_count)

# average day of resolution for issues with no assignee
print("Average day of resolution for issues without an assignee is: ",
      int(res_time_with_no_assignee/unassigned_closed_bug_count))

print("----------------Part 6----------------")
# assigned closed bugs
print("No of closed issues that had at least one assignee is: ",
      assigned_closed_bug_count)

# average day of resolution for issues with assignee
if assigned_closed_bug_count > 0:
    print("Average day of resolution for issues with at least one assignee is: ",
        int(res_time_with_assignee/assigned_closed_bug_count))
else:
    print("There are no closed issues with assignees")