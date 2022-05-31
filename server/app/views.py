from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt


# Python standard libraries
import colorsys
import json

# project package libraries
from . import git_stats
from .git_stats import GitStat
from server import token_goes_here
from server import token_goes_here
from . import timeline as timeline_generator

# Any commits that fall below this percentage of the total get added to 'other'
CONTRIBUTION_THRESHOLD = 0.01
temp_token = token_goes_here.get_user_token()


class SessionDictKey:
    REPO_OWNER = 'owner'
    REPO_NAME = 'name'
    REPO_DATA = 'data'


class Chart:
    PIE = 'pie'
    TIMELINE = 'timeline'
    CONTRIBUTOR = 'contributor'


@csrf_exempt
def index(request):
    if request.method == "POST":
        return validate_form(request, request.POST.get('url'))
    else:
        return render(request, 'index.html')


def validate_form(request, url):
    try:
        # splice the input url from the text field
        directories = list(filter(None, url[8:].split('/')))
        redirect_url = '/getData?repoOwner={owner}&repoName={name}'.format(owner=directories[1],
                                                                           name=directories[2])

        request.session[SessionDictKey.REPO_OWNER] = directories[1]
        request.session[SessionDictKey.REPO_NAME] = directories[2]

        response = redirect(redirect_url)
        return response
    except Exception as e:
        return render(request, 'index.html', {'feedback': "This URL is invalid"})


@csrf_exempt
def get_data(request):
    if request.method == "POST":
        return validate_form(request, request.POST.get('url'))
    else:
        repo_owner, repo_name = request.GET.get('repoOwner', None), request.GET.get('repoName', None)

        # Assert that the query string hasn't changed while processing
        # Also allows for the user to change the query string manually for searches
        if repo_owner != request.session[SessionDictKey.REPO_OWNER] \
                or repo_name != request.session[SessionDictKey.REPO_NAME]:
            return redirect(str(request.get_full_path()))

        assert type(repo_owner) is not None, "Repo owner not specified"
        assert type(repo_name) is not None, "Repo name not specified"

        try:
            git_stat = git_stats.get_example_of_stats(repo_owner, repo_name)
            data = json.loads(git_stat)
            assert type(data) is not None
            request.session[SessionDictKey.REPO_DATA] = data
            timeline_generator.output_timeline(timeline_generator.top_ten(timeline_generator.separate_to_dict(
                data[GitStat.COUNT_ADDITIONS_DELETIONS],
                data[GitStat.PER_WEEK_CONTRIBUTOR])))
            timeline_generator.write_to_html()
            request.session.modified = True

            redirect_url = '/displayData?type={chart_type}&repoOwner={owner}&repoName={name}/'.format(chart_type=Chart.PIE,
                                                                                                      owner=repo_owner,
                                                                                                      name=repo_name)
            return redirect(redirect_url)
        except Exception as e:
           return render(request, 'index.html', {'feedback': "This URL does not exist"})


@csrf_exempt
def display_data(request):
    if request.method == "POST":
        return validate_form(request, request.POST.get('template_search'))
    repo_owner, repo_name = request.GET.get('repoOwner', None), request.GET.get('repoName', None)

    # Assert that the query string hasn't changed while processing
    # Also allows for the user to change the query string manually for searches
    if repo_owner != request.session[SessionDictKey.REPO_OWNER] \
            or repo_name != request.session[SessionDictKey.REPO_NAME]:
        request.session[SessionDictKey.REPO_OWNER] = repo_owner
        request.session[SessionDictKey.REPO_NAME] = repo_name
        return redirect(str(request.get_full_path()), permanent=True)

    request.session[SessionDictKey.REPO_OWNER] = repo_owner
    request.session[SessionDictKey.REPO_NAME] = repo_name

    repo_data = request.session[SessionDictKey.REPO_DATA]
    owner_name = repo_data[GitStat.NAME_OWNER]
    repo_name = repo_data[GitStat.NAME_REPO]
    repo_created_date = repo_data[GitStat.REPO_DATE_CREATED]
    repo_description = repo_data[GitStat.REPO_DESCRIPTION]
    repo_updated_date = repo_data[GitStat.REPO_DATE_LAST_UPDATED]

    data_pack = {'owner_name': owner_name,
                 'repo_name': repo_name,
                 'repo_created_date': repo_created_date,
                 'repo_updated_date': repo_updated_date,
                 'repo_description': repo_description}

    if request.GET.get('type') == Chart.PIE:
        return pie_chart(request, data_pack)
    elif request.GET.get('type') == Chart.TIMELINE:
        return timeline(request, data_pack)
    elif request.GET.get('type') == Chart.CONTRIBUTOR:
        return contributor(request, data_pack)
    else:
        return render(request, 'index.html', {'feedback': "Invalid specified chart type"})


@csrf_exempt
def timeline(request, data_pack):
    return render(request, 'timeline.html', data_pack)


@csrf_exempt
def contributor(request, data_pack):
    contributor_page = request.session[SessionDictKey.REPO_DATA][GitStat.CONTRIBUTOR_PAGE]

    contributor_page.sort(reverse=False, key=lambda x: x[1].lower())
    for value in contributor_page:
        print(value[1])
    contributor_names = []
    contributor_urls = []
    contributor_emails = []
    contributor_created_at = []
    contributor_issues_opened = []
    contributor_issues_assigned = []
    contributor_repos = []

    for cont in contributor_page:
        contributor_names.append(cont[1])
        contributor_urls.append(cont[2])
        if cont[3] is not None:
            contributor_emails.append(cont[3])
        else:
            contributor_emails.append('private email')
        contributor_created_at.append(cont[4])
        contributor_issues_opened.append(cont[5])
        contributor_issues_assigned.append(cont[6])
        contributor_repos.append(cont[7])

    data_pack.update({
        "contributor_names": contributor_names,
        "contributor_emails": contributor_emails,
        "contributor_urls": contributor_urls,
        "contributor_created_at": contributor_created_at,
        "contributor_issues_opened": contributor_issues_opened,
        "contributor_issues_assigned": contributor_issues_assigned,
        "contributor_repos": contributor_repos
    })
    return render(request, 'contributor.html', data_pack)


@csrf_exempt
def pie_chart(request, data_pack):
    repo_data = request.session[SessionDictKey.REPO_DATA]
    contributor_additions_deletions = repo_data[GitStat.COUNT_ADDITIONS_DELETIONS]

    data_labels = []
    last_commit_dt = []
    commits = []
    insertions = []
    deletions = []

    # Anything not within the threshold is lumped into other_data to output together.
    other_data = [0, 0, 0]
    total_commits = 0

    # sort the list by number of commits (
    contributor_additions_deletions.sort(reverse=True, key=lambda x: x[3])

    for value in contributor_additions_deletions:
        total_commits += value[3]

    # If the repo has more than 11 contributors, show the first 10 and bundle the rest into an 'Other' label
    if len(contributor_additions_deletions) > 10:
        for _index, value in enumerate(contributor_additions_deletions):
            if _index > 9:
                if len(contributor_additions_deletions) != 11:
                    other_data[0] += value[1]
                    other_data[1] += value[2]
                    other_data[2] += value[3]
            else:
                data_labels.append(value[0])
                insertions.append(value[1])
                deletions.append(value[2])
                commits.append(value[3])
                # In some cases, a bot is used to auto-update dependencies
                # and counts as a contributor with 'commits', but no actual commit date
                try:
                    last_commit_dt.append(value[4])
                except IndexError:
                    last_commit_dt.append("")
    else:
        for value in contributor_additions_deletions:
            data_labels.append(value[0])
            insertions.append(value[1])
            deletions.append(value[2])
            commits.append(value[3])
            # In some cases, a bot is used to auto-update dependencies
            # and counts as a contributor with 'commits', but no actual commit date
            try:
                last_commit_dt.append(value[4])
            except IndexError:
                last_commit_dt.append("")

    # Other is appended to the names to account for the other_data contributors if it is used
    if other_data[2] > 0:
        data_labels.append("Other")

        insertions.append(other_data[0])
        deletions.append(other_data[1])
        commits.append(other_data[2])
        last_commit_dt.append("")

    # the following code is sourced from stackoverflow which handles the creation of the data needed for
    # the pie chart and setting each section in a shuffled colour scheme.
    # code source: https://stackoverflow.com/a/876872
    N = len(data_labels)
    HSV_tuples = [(x * 1.0 / N, 0.5, 0.5) for x in range(N)]
    RGB_tuples = list(map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples))
    colours = []

    for rgb in RGB_tuples:
        colours.append('rgba({}, {}, {}, 1)'.format(int(rgb[0] * 256), int(rgb[1] * 256), int(rgb[2] * 256)))

    # Swapping colour positions for contrast as they are initially generated in a gradient
    offset = 0
    if len(colours) % 2 != 0:
        offset = 1
    for x, colour in enumerate(colours):
        if len(colours) / 2 > x + 1:
            if (x % 2) == offset:
                colours[x], colours[-x] = colours[-x], colours[x]
        else:
            break

    data_pack.update({'dataLabels': data_labels,
                      'lastCommitDT': last_commit_dt,
                      'commits': commits,
                      'backgroundColor': colours,
                      'insertions': insertions,
                      'deletions': deletions,
                      'commits_count': repo_data[GitStat.COUNT_COMMITS],
                      'contributors_count': repo_data[GitStat.COUNT_CONTRIBUTOR],
                      'open_issues_count': repo_data[GitStat.COUNT_ISSUES_OPEN],
                    #   'closed_issues_count': repo_data[GitStat.COUNT_ISSUES_CLOSED],
                      'pull_request_count': repo_data[GitStat.COUNT_PULL_REQUESTS],
                      'projects_count': repo_data[GitStat.COUNT_PROJECTS],
                      'branches_count': repo_data[GitStat.COUNT_BRANCHES],
                      'releases_count': repo_data[GitStat.COUNT_RELEASES],
                      'repo_license': repo_data[GitStat.REPO_LICENSE],
                      'subscribers_count': repo_data[GitStat.COUNT_SUBSCRIBERS],
                      'stars_count': repo_data[GitStat.COUNT_STARS],
                      'forks_count': repo_data[GitStat.COUNT_FORKS],
                      'repo_languages': repo_data[GitStat.REPO_LANGUAGES]})

    response = render(request, 'summary.html', data_pack)
    return response