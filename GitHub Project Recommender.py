#!/usr/bin/env python
# -*- coding: utf-8 -*-
from Tkinter import *
import ttk
import tkFileDialog
import sys
from recommendations import *



class GUI(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.language_info = list()
        self.selected_user_index = ''
        self.similarity = recommendations.sim_pearson

        self.label_title = Label(self, text='GitHub Project Recommender', font=('', '25', 'bold'), background='orange', foreground='white')
        self.label_title.grid(row=0, column=0, columnspan=7, sticky=E+W)
        self.label_between = Label(self, background='grey')
        self.label_between.grid(row=1, column=1, columnspan=5, sticky=E + W + N + S)

        # Upload User Data Button
        self.upload_user_data = Button(self, text='Upload User Data', relief='groove', command=Data.upload_user_data)
        self.upload_user_data.grid(row=1, column=0, sticky=E)

        # Upload Repository Data
        self.upload_repository_data = Button(self, text='Upload Repository Data', relief='groove', command=Data.upload_repo_data)
        self.upload_repository_data.grid(row=1, column=3)

        # Upload Star Data
        self.upload_star_data = Button(self, text='Upload Star Data', relief='groove', command=Data().upload_star_data)
        self.upload_star_data.grid(row=1, column=5, sticky=E)

        self.label_recommendations = Label(self, text='Recommendations')
        self.label_recommendations.grid(row=2, column=5)

        self.label_recommended_repo = Label(self, text='Recommended Repository For:')
        self.label_recommended_repo.grid(row=3, column=0)

        # Treeview of users
        self.treeview_users = ttk.Treeview(self)
        self.treeview_users.grid(row=4, column=0)
        self.treeview_users['show'] = 'headings'
        self.treeview_users['columns'] = ('0', '1')
        self.treeview_users.column('0', width=100)
        self.treeview_users.heading('0', text='Username')
        self.treeview_users.column('1', width=50)
        self.treeview_users.heading('1', text='Id')
        self.treeview_users.bind('<<TreeviewSelect>>', self.treeview_selection)
        self.scrollbar_users = Scrollbar(self, orient=VERTICAL)
        self.treeview_users['yscrollcommand'] = self.scrollbar_users.get()
        self.scrollbar_users['command'] = self.treeview_users.yview()
        self.treeview_users.config(yscrollcommand=self.scrollbar_users.set)
        self.scrollbar_users.config(command=self.treeview_users.yview)
        self.scrollbar_users.grid(row=4, column=0, sticky=E + N + S)

        self.label_filter = Label(self, text=' Filter by programming language:')
        self.label_filter.grid(row=7, column=0)

        # Combobox for programming language
        self.combobox_language = ttk.Combobox(self)
        self.combobox_language.grid(row=8, column=0)

        self.label_algorithm = Label(self, text='Distance Algorithm:')
        self.label_algorithm.grid(row=9, column=0)

        # Check Buttons
        self.check_button_pearson = Checkbutton(self, text='Pearson', command=self.switch_pearson)
        self.check_button_pearson.grid(row=10, column=0)
        self.check_button_pearson.select()
        self.check_button_euclidean = Checkbutton(self, text='Euclidean', command=self.switch_euclidean)
        self.check_button_euclidean.grid(row=11, column=0)

        self.label_num_reco = Label(self, text='Number of Recommendations:')
        self.label_num_reco.grid(row=12, column=0)

        # Entry Box
        self.entrybox_recommendations = Entry(self, width=5)
        self.entrybox_recommendations.grid(row=12, column=1)

        # Recommend Buttons
        self.recommend_repo = Button(self, text='Recommend Repository', relief='groove', command=Repository.recommend_repo)
        self.recommend_repo.grid(row=4, column=2, sticky=E + W + S)
        self.recommend_user = Button(self, text='Recommend GitHub User', relief='groove', command=GithubUser.recommend_user)
        self.recommend_user.grid(row=5, column=2, sticky=E + W + N)

        # Treeview of Recommendations
        self.treeview_recommendations = ttk.Treeview(self)
        self.treeview_recommendations.grid(row=3, rowspan=9, column=5, sticky=N + S)
        self.treeview_recommendations['show'] = 'headings'
        self.treeview_recommendations['columns'] = ('name', 'url', 'score')
        self.treeview_recommendations.column('name', width=100)
        self.treeview_recommendations.heading('name', text='Name')
        self.treeview_recommendations.column('url', width=200)
        self.treeview_recommendations.heading('url', text='Url')
        self.treeview_recommendations.column('score', width=50)
        self.treeview_recommendations.heading('score', text='Score')
        self.scrollbar_recommendations = Scrollbar(self, orient=VERTICAL)
        self.treeview_recommendations['yscrollcommand'] = self.scrollbar_recommendations.get()
        self.scrollbar_recommendations['command'] = self.treeview_recommendations.yview()
        self.treeview_recommendations.config(yscrollcommand=self.scrollbar_recommendations.set)
        self.scrollbar_recommendations.config(command=self.treeview_recommendations.yview)
        self.scrollbar_recommendations.grid(row=3, rowspan=9, column=6, sticky=E + N + S)

        self.grid()

    def switch_pearson(self):  # if pearson is selected, it deselects euclidean option
        if self.check_button_pearson:
            self.check_button_euclidean.deselect()
            self.similarity = recommendations.sim_pearson

    def switch_euclidean(self):  # if euclidean is selected, it deselects pearson option
        if self.check_button_euclidean:
            self.check_button_pearson.deselect()
            self.similarity = recommendations.sim_distance

    def treeview_selection(self, event):  # This function is for getting id for selected user
        item = self.treeview_users.selection()[0]
        self.selected_user_index = self.treeview_users.item(item, 'text')


class Repository:
    def __init__(self, repo_id, repo_name, repo_url, language):
        self.repo_id = repo_id
        self.repo_name = repo_name
        self.repo_url = repo_url
        self.language = language
        self.score = 5.0

    @staticmethod
    def recommend_repo():
        Data().critic_dictionary()
        app.treeview_recommendations.delete(*app.treeview_recommendations.get_children())
        critics = recommendations.transformPrefs(Data.critics)
        results = list()
        recommended_projects = recommendations.getRecommendations(critics, int(app.selected_user_index), similarity=app.similarity)
        for info in recommended_projects:
            language = Data.projects[info[1]].language.strip('\n')
            if language == app.combobox_language.get():
                results.append(info)
        for i in results[:int(app.entrybox_recommendations.get())]:
            app.treeview_recommendations.insert("", END, values=(Data.projects[i[1]].repo_name, Data.projects[i[1]].repo_url, i[0]))

    # This method, transforms the current dictionary for repositories then checks the results from getRecommendations function
    # one by one. If the language attribute of the project is equals to value of combobox then it puts in to a list which name is results.
    # From the result list it inserts to the recommendations treeview


class GithubUser:
    def __init__(self, user_id, user_name, user_url):
        self.user_id = user_id
        self.user_name = user_name
        self.user_url = user_url

    @staticmethod
    def recommend_user():
        Data().critic_dictionary()
        app.treeview_recommendations.delete(*app.treeview_recommendations.get_children())
        recommended_users = recommendations.topMatches(Data.critics, int(app.selected_user_index), int(app.entrybox_recommendations.get()), similarity=app.similarity)
        for info in recommended_users:
            app.treeview_recommendations.insert("", END, values=(Data.users[info[1]].user_name, Data.users[info[1]].user_url, info[0]))
    # This method calls the function for creating dictionary then with results from the topMatches functions
    # It inserts to the treeview for recommendations


class Data:
    users = dict()
    critics = dict()
    projects = dict()
    star_info = list()

    def __init__(self):
        pass

    @staticmethod
    def upload_user_data():
        user_info = list()
        file_path = tkFileDialog.askopenfilename(initialdir="/", title="User Data:")
        user_data_file = open(file_path, 'r')
        for info in user_data_file.readlines():
            user_info.append([info.split(',')[1].lower(), info.split(',')[0], info.split(',')[2]])
        user_info.sort()

        for info in user_info:
            app.treeview_users.insert("", END, values=info, text=int(info[1]))

        user_data_file.close()

        for i in range(len(user_info)):
            Data.users[int(user_info[i][1])] = (GithubUser(user_info[i][1], user_info[i][0], user_info[i][2]))
    # This method reads data from a text file and inserts users to the treeview of users
    # Also, it turns them into objects through GithubUser class

    @staticmethod
    def upload_repo_data():
        repo_info = list()
        language_info = list()
        file_path = tkFileDialog.askopenfilename(initialdir="/", title="User Data:")
        repo_data_file = open(file_path, 'r')
        for info in repo_data_file.readlines():
            repo_info.append(info.split(','))
            language = info.split(',')[3]
            language_info.append(language.strip('\n'))
        language_info = list(set(language_info))
        app.language_info = ['None']+sorted(language_info, key=str.lower)
        app.combobox_language['values'] = app.language_info
        app.combobox_language.current(0)

        repo_data_file.close()
        for i in range(len(repo_info)):
            Data.projects[int(repo_info[i][0])] = (Repository(repo_info[i][0], repo_info[i][1], repo_info[i][2], repo_info[i][3]))
    # This method is reads a text file and clears the data for the usage.
    # And it makes a sorted list of the languages of the program then it puts it into the combobox
    # Finally, it turns the information to the objects through Repository class

    def upload_star_data(self):
        file_path = tkFileDialog.askopenfilename(initialdir="/", title="User Data:")
        star_data_file = open(file_path, 'r')
        i = 0
        for info in star_data_file.readlines():
            star_info = info.split('\t')
            star_info = ([i] + [list(star_info[1].split(','))])
            self.star_info.append(star_info)
            i += 1

        star_data_file.close()
    # This method is reading the text file and puts the information into a list later on it will be used for creating a dictionary

    def critic_dictionary(self):
        for i in range(len(Data.users.values())):
            ratings = dict()
            for repo_id in self.star_info[i][1]:
                ratings[int(repo_id)] = 5.0
            self.critics.setdefault(i, ratings)
    # This method is using the related information about users, repository, and ratings and puts them into a into a dictionary


def main():
    global app
    root = Tk()
    root.title = "Github Repository Recommender"
    root.geometry()
    app = GUI(root)
    root.mainloop()


main()