from server import token_goes_here

from github import Github

import json
import requests

token = token_goes_here.get_user_token()


# Definition of keys for the data structure
class GitStat:
    COUNT_CONTRIBUTOR = "contributors_count"
    COUNT_COMMITS = "commits_count"
    COUNT_ISSUES_OPEN = "open_issues_count"
    COUNT_ISSUES_CLOSED = "closed_issues_count"
    COUNT_PULL_REQUESTS = "pull_request_count"
    COUNT_PROJECTS = "projects_count"
    COUNT_BRANCHES = "branches_count"
    COUNT_RELEASES = "releases_count"
    COUNT_SUBSCRIBERS = "subscribers_count"
    COUNT_STARS = "stars_count"
    COUNT_FORKS = "forks_count"
    COUNT_ADDITIONS_DELETIONS = "number_of_addition_deletion"

    NAME_OWNER = "owner_name"
    NAME_REPO = "repo_name"

    CONTRIBUTIONS_PER_WEEK = "number_of_week"
    PER_WEEK_CONTRIBUTOR = "weekly_contributions"
    CONTRIBUTOR_PAGE = "contributor_page"

    REPO_CONTRIBUTORS = "contributors"
    REPO_DESCRIPTION = "repo_description"
    REPO_CONTRIBUTOR_RATIO = "percentage_per_contributor"
    REPO_LICENSE = "repo_license"
    REPO_DATE_CREATED = "repo_created_date"
    REPO_DATE_LAST_UPDATED = "repo_updated_date"
    REPO_LANGUAGES = "repo_languages"
    C_LOGINS = "c_logins"
    C_URL = "c_url"
    C_EMAIL = "c_email"
    c_JOINED = "c_joined"
    C_CREATED_ISSUES = "c_created_issues"
    C_ASSIGNED_ISSUES = "c_assigned_issues_per"
    C_REPOS_INVOLVED = "c_repos_involved"


def get_example_of_stats(user, repo):
    """
    This function returns a Json object which is used for extracting the information needed.
    This is not the final function but rather the function that we will use for testing purposes until we design the
    complete function to be used for the Web App.
    :user: The user needed to access the repository.
    :repo: The repository itself as it is taken from the string.
    :return: Json string in the form of a dictionary for use later.
    """

    # Needed in future.
    data = ""

    # The following are some of the statistics that will eventually be needed.

    # Setting the repository object as retrieved from the Github library via the token given.
    git_stats = Github(token)

    # Setting the repository alone as a separate variable to be used for extracting the necessary information.
    git_repo = git_stats.get_repo(user + "/" + repo)

    stats_dict = {}

    # table in summary page
    contributors = git_repo.get_stats_contributors()

    # this is used to retrieve any issues from the repository, but only open ones are taken.
    open_issues_count = git_repo.open_issues_count
    closed_issues = git_repo.get_issues(state="closed")
    created_date = git_repo.created_at
    updated_date = git_repo.updated_at
    pull_request = git_repo.get_pulls()
    projects = git_repo.get_projects()
    try:
        stats_dict[GitStat.COUNT_PROJECTS] = str(projects.totalCount)
    except Exception:
        stats_dict[GitStat.COUNT_PROJECTS] = str(0)
    branches = git_repo.get_branches()
    releases = git_repo.get_releases()
    subscribers_count = git_repo.subscribers_count
    stars_count = git_repo.stargazers_count
    forks_count = git_repo.forks_count
    repo_description = git_repo.description
    commits = git_repo.get_commits()

    repo_languages = git_repo.get_languages()
    top_languages = ""
    temp = []
    for key, value in repo_languages.items():
        temp.append((value,key))

    temp = sorted(temp)
    temp = temp[::-1]

    for i in range(len(temp)):
        if i == 3:
            break
        top_languages += temp[i][1]+", "
    top_languages = top_languages[0:len(top_languages)-2]

    repo_languages  = git_repo.get_languages()
    top_languages  = ""
    temp = []
    for key, value in repo_languages.items():
        temp.append((value,key))

    temp = sorted(temp)
    temp = temp[::-1]

    for i in range(len(temp)):
        if i == 3:
            break
        top_languages += temp[i][1]+", "
    top_languages = top_languages[0:len(top_languages)-2]

    repo_name = git_repo.name
    owner_name = git_repo.owner.login
    try:
        repo_license = git_repo.get_license().license.key
    except Exception as e:
        repo_license = "None"

    ##### Jay, this is a list of dict entries if you want them like this
    contributor_page = []
    # each entry consists of name, page url, email, joined date, created issues, assigned issues, list of repos
    for c in contributors:
        repos = requests.get(c.author.repos_url, headers={"Authorization": "token " + token}).json()
        parsed = []
        for repo in repos:
            parsed.append(repo["name"])
        contributor_page.append([
            c.author.name,
            c.author.login,
            c.author.html_url,
            c.author.email,
            str(c.author.created_at),
            git_repo.get_issues(state="open", creator= c.author.login).totalCount,
            git_repo.get_issues(state="open", assignee= c.author.login).totalCount,
            parsed
            ])

    stats_dict[GitStat.CONTRIBUTOR_PAGE] = contributor_page


    # Assigning the variable total commits before using in loop as is necessary.
    total_commits = get_total_commits(contributors)

    # Adding the total value (all commits) of each contributor as a number which is added to the total commits over
    # which the percentage will be worked out.
    # for i in range(len(contributors)):
    #     total_commits += contributors[i]._total.value

    # Starting the dictionary that will be returned at the end of the function for Pie Chart use.

    # TODO: Please get rid of any hard-coded strings and replace them with 'static' variables.
    # Eventually, all strings will be declared near the top and will be used as variables once we need to print them.
    stats_dict[GitStat.REPO_CONTRIBUTORS] = [contributors[i].author.login for i in range(len(contributors))]

    # A for loop is used to work out the decimal gained from dividing the contributors commits by the total, it is
    # rounded for ease of use.
    contributors_ratio = get_contributor_ratio(contributors, total_commits)
    stats_dict[GitStat.REPO_CONTRIBUTOR_RATIO] = [contributors_ratio]

    stats_dict[GitStat.COUNT_CONTRIBUTOR] = len(contributors)
    stats_dict[GitStat.COUNT_COMMITS] = str(total_commits)
    stats_dict[GitStat.COUNT_ISSUES_OPEN] = str(open_issues_count)
    # stats_dict[GitStat.COUNT_ISSUES_CLOSED] = str(closed_issues.totalCount)
    stats_dict[GitStat.REPO_LANGUAGES] = top_languages
    stats_dict[GitStat.COUNT_PULL_REQUESTS] = str(pull_request.totalCount)
    stats_dict[GitStat.COUNT_BRANCHES] = str(branches.totalCount)
    stats_dict[GitStat.COUNT_RELEASES] = str(releases.totalCount)
    stats_dict[GitStat.COUNT_SUBSCRIBERS] = str(subscribers_count)
    stats_dict[GitStat.COUNT_STARS] = str(stars_count)
    stats_dict[GitStat.COUNT_FORKS] = str(forks_count)
    stats_dict[GitStat.REPO_DESCRIPTION] = repo_description

    stats_dict[GitStat.NAME_OWNER] = str(owner_name)
    stats_dict[GitStat.NAME_REPO] = str(repo_name)
    stats_dict[GitStat.REPO_LICENSE] = str(repo_license)

    # stats_dict[GitStat.C_LOGINS] = c_logins
    # stats_dict[GitStat.C_URL] = c_url
    # stats_dict[GitStat.C_EMAIL] = c_email
    # stats_dict[GitStat.c_JOINED] = c_joined
    # stats_dict[GitStat.C_CREATED_ISSUES] = c_created_issues
    # stats_dict[GitStat.C_ASSIGNED_ISSUES] = c_assigned_issues
    # stats_dict[GitStat.C_REPOS_INVOLVED] = c_repos_involved

    contribution = get_commit_add_del(contributors)

    per_contributors = contribution[1]
    per_week_contributors = contribution[0]
    git_stats.per_page = 1
    get_last_commit(per_contributors, commits)
    number_of_week = contribution[2]
    # for i in range(len(contributors)):
    #     addition = 0
    #     deletion = 0
    #     commit = 0
    #     number_of_week = len(contributors[i].weeks)
    #     # loop through each week and add the addition and deletion of the contributor to a total
    #     for j in range(len(contributors[i].weeks)):
    #         addition = addition + contributors[i].weeks[j].a  # addition
    #         deletion = deletion + contributors[i].weeks[j].d  # deletion
    #         commit = commit + contributors[i].weeks[j].c  # commit
    #         per_week_contributors.append([j, [contributors[i].author.login, contributors[i].weeks[j].a,
    #                                           contributors[i].weeks[j].d, contributors[i].weeks[j].c]])
    #     per_contributors.append([contributors[i].author.login, addition, deletion, commit])

    stats_dict[GitStat.PER_WEEK_CONTRIBUTOR] = per_week_contributors
    stats_dict[GitStat.COUNT_ADDITIONS_DELETIONS] = per_contributors
    stats_dict[GitStat.REPO_DATE_CREATED] = created_date.strftime("%d/%m/%Y, %H:%M:%S")
    stats_dict[GitStat.REPO_DATE_LAST_UPDATED] = updated_date.strftime("%d/%m/%Y, %H:%M:%S")

    stats_dict[GitStat.COUNT_ADDITIONS_DELETIONS] = per_contributors
    stats_dict[GitStat.REPO_DATE_CREATED] = created_date.strftime("%m/%d/%Y, %H:%M:%S")
    stats_dict[GitStat.REPO_DATE_LAST_UPDATED] = updated_date.strftime("%m/%d/%Y, %H:%M:%S")

    # for x, contributor in enumerate(per_contributors):
    #     commits = git_repo.get_commits(author=contributor[0])
    #     if commits.totalCount > 0:
    #         last_commit = commits[0]
    #         date = 'Last Commit: ' + str(last_commit.commit.author.date)
    #         per_contributors[x].append(date)

    # stats_dict[GitStat.CONTRIBUTIONS_PER_WEEK] = number_of_week

    # Adding the read_me from above. Commented out as unused currently.
    # stats_dict["Readme"] = read_me.decoded_content

    return json.dumps(stats_dict)


def get_commit_add_del(contributors):
    per_contributors = []
    per_week_contributors = []
    number_of_week = 0
    for i in range(len(contributors)):
        addition = 0
        deletion = 0
        commit = 0
        number_of_week = len(contributors[i].weeks)
        # loop through each week and add the addition and deletion of the contributor to a total
        for j in range(len(contributors[i].weeks)):
            addition = addition + contributors[i].weeks[j].a  # addition
            deletion = deletion + contributors[i].weeks[j].d  # deletion
            commit = commit + contributors[i].weeks[j].c  # commit
            per_week_contributors.append([j, [contributors[i].author.login, contributors[i].weeks[j].a,
                                              contributors[i].weeks[j].d, contributors[i].weeks[j].c]])
            # print(contributors[i].weeks[j].a)
            # print(contributors[i].weeks[1].d)
            per_week_contributors.append([j, [contributors[i].author.login, contributors[i].weeks[j].a, contributors[i].weeks[j].d, contributors[i].weeks[j].c]])
        per_contributors.append([contributors[i].author.login, addition, deletion, commit])
    # print(per_contributors)
    # print(per_week_contributors)
    # print(number_of_week)

    return per_week_contributors, per_contributors, number_of_week


def get_last_commit(per_contributors, commits):
    for x, contributor in enumerate(per_contributors):
        # commits = git_repo.get_commits(author=contributor[0])
        if commits.totalCount > 0:
            last_commit = commits[0]
            date = 'Last Commit: ' + str(last_commit.commit.author.date)
            per_contributors[x].append(date)


def get_total_commits(contributors):
    total_commits = 0
    for i in range(len(contributors)):
        total_commits += contributors[i]._total.value
    return total_commits


def get_contributor_ratio(contributors, total_commits):
    arr = []
    percent = 100
    accuracy = 2
    for i in range(len(contributors)):
        arr.append(
            (contributors[i].author.login, round((contributors[i]._total.value / total_commits) * percent, accuracy)))
    return arr
