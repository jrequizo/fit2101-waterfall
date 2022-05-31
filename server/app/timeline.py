"""
Bokeh Visualization Template
This template is a general outline for turning your data into a
visualization using Bokeh.
"""

# Bokeh libraries (might be needed for interactivity).
from bokeh.plotting import figure, show
from bokeh.io import save

from html.parser import HTMLParser


# Joins the two individual lists into a dictionary for usage.


def separate_to_dict(per_contributor, per_week_contributor):

    """
    Converts the per_contributors and per_week_contributors into the dictionary format in the format that is needed, for
    the rest of the functions to work with it.
    :return: A dictionary with 'Summary' and 'Weeks'.
    """

    if len(per_contributor[0]) > 4:
        for i in range(len(per_contributor)):
            per_contributor[i].pop()

    weeks = [['Week {}'.format(i + 1)] for i in range(int(len(per_week_contributor) / len(per_contributor)))]

    for j in range(len(weeks)):
        for i in range(0, len(per_week_contributor), len(weeks)):
            if i + j >= len(per_week_contributor):
                index = len(per_week_contributor) - 1
            else:
                index = i + j
            weeks[j].append(per_week_contributor[index][1])
    return {'Summary': per_contributor, 'Weeks': weeks}


# Condensed into top 10 major contributors.


def top_ten(diction):
    diction2 = dict(diction)
    diction3 = dict(diction)
    contributoress = diction2['Summary']
    index = 0
    commits = 3
    current_highest = contributoress[index][commits]
    highest_summary = []
    highest_contributors = []

    if len(contributoress) > 11:
        for i in range(10):
            j = 0

            while j < len(contributoress):
                if contributoress[j][3] > current_highest:
                    current_highest = contributoress[j][commits]
                    index = j
                else:
                    j += 1
            highest_contributors.append(contributoress[index][0])
            highest_summary.append(contributoress[index])
            contributoress.pop(index)
            current_highest = 0
        others_summary = ['Other', 0, 0, 0]

        for i in range(len(contributoress)):
            others_summary[1] += contributoress[i][1]
            others_summary[2] += contributoress[i][2]
            others_summary[3] += contributoress[i][3]

        highest_summary.append(others_summary)
        highest_contributors.append(others_summary[0])
        diction3['Summary'] = highest_summary

        for i in range(len(diction3['Weeks'])):
            j = 1
            while j < len(diction3['Weeks'][i]):
                if diction3['Weeks'][i][j][0] not in highest_contributors:
                    #print(highest_contributors)
                    #print(diction3['Weeks'][i])
                    diction3['Weeks'][i].pop(j)
                else:
                    j += 1

        for i in range(len(diction2['Weeks'])):
            current = ['Other', 0, 0, 0]
            for j in range(1, len(diction2['Weeks'][i])):
                if diction2['Weeks'][i][0] not in highest_contributors:
                    current[1] += diction2['Weeks'][i][j][1]
                    current[2] += diction2['Weeks'][i][j][2]
                    current[3] += diction2['Weeks'][i][j][3]
            diction3['Weeks'][i].append(current)
        return diction3

    else:
        return diction


# y-axis creation for the timeline.


def y_axis_creation(dict_contribute):

    """
    Creates the y-axis list needed for the timeline which shows the contributors, makes a list with the name in the
    correct coordinate or not if they did no work. Needs to take in a dictionary with the correct information.
    :param dict_contribute: Uses Summary from the dictionary and the weekly work.
    :return: A usable list for the y-axis.
    """

    # Makes a list of contributors.
    contributors_list = []
    for i in range(len(dict_contribute['Summary'])):
        contributors_list.append(dict_contribute['Summary'][i][0])

    # Adds the week they worked in in the correct location on the list.
    y_axis_list = []
    for i in range(len(dict_contribute['Weeks'])):
        for j in range(len(dict_contribute['Summary'])):

            # Checks whether or not they contributed.
            if dict_contribute['Weeks'][i][j + 1][1] > 0:
                y_axis_list.append(dict_contribute['Summary'][j][0])
            elif dict_contribute['Weeks'][i][j + 1][2] > 0:
                y_axis_list.append(dict_contribute['Summary'][j][0])
            elif dict_contribute['Weeks'][i][j + 1][3] > 0:
                y_axis_list.append(dict_contribute['Summary'][j][0])
            else:
                y_axis_list.append('None')

    return y_axis_list, contributors_list


# x-axis creation for the timeline.


def x_axis_creation(dict_contribute):

    """
    Takes the same dictionary as input for the y-axis and extracts the number of weeks then makes a new list
    that contains the weeks squared which is used for the x-axis.
    :param dict_contribute: Uses the Weeks in this dictionary.
    :return: Returns the usable list.
    """

    # A normal list of the weeks.
    weeks_list = []
    for i in range(len(dict_contribute['Weeks'])):
        weeks_list.append('Week {}'.format(i + 1))

    # The list of weeks squared.
    x_axis_list = []
    for i in range(len(weeks_list)):
        for j in range(len(dict_contribute['Summary'])):
            x_axis_list.append(weeks_list[i])

    return x_axis_list, weeks_list


# Colour list creation.


def colour_creation(weeks_list, contributors_list):

    """
    Goes through the number of contributors and weeks and creates a list that makes a colour per contributor and
    puts them in a list where they match a coordinate. They can be used if the person worked or not.
    :param weeks_list: The list of needed weeks.
    :param contributors_list: The list of needed contributors.
    :return: A coordinated list of colurs.
    """

    colours = ['dimgray', 'lightslategray', 'papayawhip', 'darkslategray', 'black', 'lightsteelblue', 'powderblue',
               'lightblue', 'skyblue', 'lightskyblue', 'deepskyblue', 'dodgerblue', 'cornflowerblue', 'steelblue',
               'royalblue', 'blue', 'mediumblue', 'darkblue', 'navy', 'midnightblue', 'cornsilk', 'blanchedalmond',
               'bisque', 'navajowhite', 'wheat', 'burlywood', 'tan', 'rosybrown', 'sandybrown', 'goldenrod',
               'darkgoldenrod', 'peru', 'chocolate', 'saddlebrown', 'sienna', 'brown', 'maroon', 'mediumaquamarine',
               'aqua', 'cyan', 'lightcyan', 'paleturquoise', 'aquamarine', 'turquoise', 'mediumturquoise',
               'darkturquoise', 'lightseagreen', 'cadetblue', 'darkcyan', 'teal', 'darkolivegreen', 'olive',
               'olivedrab', 'yellowgreen', 'limegreen', 'lime', 'lawngreen', 'chartreuse', 'greenyellow', 'springgreen',
               'mediumspringgreen', 'lightgreen', 'palegreen', 'darkseagreen', 'mediumseagreen', 'seagreen',
               'forestgreen', 'green', 'darkgreen', 'orangered', 'tomato', 'coral', 'darkorange', 'orange', 'pink',
               'lightpink', 'hotpink', 'deeppink', 'palevioletred', 'mediumvioletred', 'lavender', 'thistle', 'plum',
               'violet', 'orchid', 'fuchsia', 'magenta', 'mediumorchid', 'mediumpurple', 'blueviolet', 'darkviolet',
               'darkorchid', 'darkmagenta', 'purple', 'indigo', 'darkslateblue', 'slateblue', 'mediumslateblue',
               'salmon', 'darksalmon']
    colour_list = []

    for i in range(len(weeks_list)):
        for j in range(len(contributors_list)):
            colour_list.append(colours[j])

    return colour_list


# To output the file.


def output_timeline(diction):
    y_axis = y_axis_creation(diction)
    x_axis = x_axis_creation(diction)
    colours_created = colour_creation(x_axis[1], y_axis[1])

    # Creates the figure via Bokeh.
    hm = figure(title="Timeline", tools="hover", toolbar_location=None, x_range=x_axis[1], y_range=y_axis[1])
    hm.sizing_mode = 'scale_width'

    # Inputs the information into the figure.
    hm.rect(x_axis[0], y_axis[0], color=colours_created, width=1, height=1)

    # Saves it to a static HTML file.
    save(hm, title="Timeline", filename='TimelineFig.html')
    #output_file("TimelineFig.html", title="Timeline")


# To combine the timeline generated HTML file into the will-be-rendered timeline page HTML file.


def write_to_html():
    # clear out the old content first

    temp_lines = []
    with open("app/templates/timeline.html") as timeline_page:
        temp_lines = timeline_page.readlines()

    file = ''.join(temp_lines)

    start_div = '<div class="w3-container" id="startdiv">'
    start_index = file.index(start_div, 1)
    start_length = len(start_div)

    end_div = '</div><div class="w3-container" id="enddiv">'
    end_index = file.index(end_div, 1)
    end_length = len(end_div)

    with open("TimelineFig.html") as timeline_figure:
        body = False
        body_strs = []
        line_in_fig = timeline_figure.readline()

        while line_in_fig:
            line_in_fig = timeline_figure.readline()

            if line_in_fig.__contains__('<body>'):
                body = True
            elif line_in_fig.__contains__('</html>'):
                body = False
            if body is True:
                body_strs.append(line_in_fig)

    body_strs.pop(0)

    for i in range(2):
        body_strs.pop()

    string = ''
    for j in range(len(body_strs)):
        string += body_strs[j]

    file = file[:start_index + start_length] + string + file[end_index:]
    with open('app/templates/timeline.html', 'w') as timeline_page:
        timeline_page.seek(0)
        timeline_page.write(file)
        timeline_page.truncate()