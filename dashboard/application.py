import os

from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError

import pandas as pd
import numpy as np
import spacy
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from math import pi
import plotly.express as px
import plotly.io as pio
import seaborn as sns
import pygal
from pygal.style import Style
from wordcloud import WordCloud
from sklearn.feature_extraction import text 
import spacy
import io
import base64
from base64 import b64encode


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Read Data
data = pd.read_pickle("..\\pickle\\main_data.pkl")
data_clean = pd.read_pickle("..\\pickle\\corpus.pkl")

data["Share"] = data["Share"].apply(lambda x: int(x))
    
@app.route("/")
def index():
    return render_template('index.html')

@app.route("/dashboard")
def dashboard():
    
    # Total Confessions
    TOTAL_CONFESSIONS = data.shape[0]
    
    # Maximum Comments
    MAX_COMMENTS = data["Comment"].max()
    
    # Maximum Shares
    MAX_SHARES = data["Share"].max()
    
    # Maximum Reactions
    MAX_REACTIONS = data["Total Reactions"].max()

    # Total Category
    df_cat = pd.DataFrame(data[['Advice', 'Ask Prof Ben', 'Funny', 'Lost and Found', 'Nostalgia', 'Rant', 'Romance']].sum(axis=0)).reset_index()
    df_cat.columns = ["Category", "Total"]
    
    series_total_cat = df_cat.groupby("Category")["Total"].sum()
    barChart_cat = pygal.HorizontalBar(height=300, width=500)
    [barChart_cat.add(x[0], x[1]) for x in series_total_cat.items()]
    barChart_cat.title = 'Total # of confessions'
    GRAPH_DATA_CATEGORY = barChart_cat.render_data_uri()
    
    # Total Reaction
    df_reaction = pd.DataFrame(data[['Angry', 'Care', 'Haha', 'Like', 'Love', 'Sad', 'Wow']].sum(axis=0)).reset_index()
    df_reaction.columns = ["Reaction", "Total"]
    
    series_total_reaction = df_reaction.groupby("Reaction")["Total"].sum()
    barChart_reaction = pygal.HorizontalBar(height=300, width=500)
    [barChart_reaction.add(x[0], x[1]) for x in series_total_reaction.items()]
    barChart_reaction.title = 'Total # of reactions'
    GRAPH_DATA_REACTION = barChart_reaction.render_data_uri()
    
    # Post with max comments
    POST_MAX_COMMENTS = data.loc[data["Comment"] == MAX_COMMENTS]["Content"].values[0]
    
    # Post with max shares
    POST_MAX_SHARES = data.loc[data["Share"] == MAX_SHARES]["Content"].values[0]
    
    # Post with max reactions
    POST_MAX_REACTIONS = data.loc[data["Total Reactions"] == MAX_REACTIONS]["Content"].values[0]
    
    # Most angry post
    POST_ANGRY = data.loc[data["Angry"] == data["Angry"].max()]["Content"].values[0]
    
    # Most caring post
    POST_CARE = data.loc[data["Care"] == data["Care"].max()]["Content"].values[0]
    
    # Most haha post
    POST_HAHA = data.loc[data["Haha"] == data["Haha"].max()]["Content"].values[0]
    
    # Most like post
    POST_LIKE = data.loc[data["Like"] == data["Like"].max()]["Content"].values[0]
    
    # Most love post
    POST_LOVE = data.loc[data["Love"] == data["Love"].max()]["Content"].values[0]
    
    # Most sad post
    POST_SAD = data.loc[data["Sad"] == data["Sad"].max()]["Content"].values[0]
    
    # Most wow post
    POST_WOW = data.loc[data["Wow"] == data["Wow"].max()]["Content"].values[0]
    
    

    return render_template('dashboard.html', graph_data_category=GRAPH_DATA_CATEGORY,
                             graph_data_reaction = GRAPH_DATA_REACTION,
                             total_confessions = TOTAL_CONFESSIONS,
                             max_comments = MAX_COMMENTS,
                             max_shares = MAX_SHARES,
                             max_reactions = MAX_REACTIONS,
                             post_max_comments = POST_MAX_COMMENTS,
                             post_max_shares = POST_MAX_SHARES,
                             post_max_reactions = POST_MAX_REACTIONS,
                             post_angry = POST_ANGRY,
                             post_care = POST_CARE,
                             post_haha = POST_HAHA,
                             post_like = POST_LIKE,
                             post_love = POST_LOVE,
                             post_sad = POST_SAD,
                             post_wow = POST_WOW
                             )

@app.route("/explore", methods=['GET', 'POST'])
def explore():
    
    # Define Categories
    REACTION_TYPE = ["Angry", "Care", "Haha", "Like", "Love", "Sad", "Wow", "No Reactions"]
    CATEGORY_TYPE = ["Advice", "Ask Prof Ben", "Funny", "Lost and Found", "Nostalgia", "Rant", "Romance", "No Category"]
    SORT_TYPE = ["Comment", "Share", "Angry", "Care", "Haha", "Like", "Love", "Sad", "Wow", "Total Reactions"]

    if request.method == "POST":
        selected_reaction = request.form.getlist("reaction_check")
        selected_category = request.form.getlist("category_check")
        selected_sorting = request.form.get("sort_check")
        
        # Check parameters
        if len(selected_category) == 0:
            flash("Please select a category!")
            return render_template("explore.html", reaction_type=REACTION_TYPE, category_type=CATEGORY_TYPE, sort_type=SORT_TYPE)
        
        if selected_sorting == None:
            flash("Please select a sort type!")
            return render_template("explore.html", reaction_type=REACTION_TYPE, category_type=CATEGORY_TYPE, sort_type=SORT_TYPE)
        
        reference = []
        for category in selected_category:
            reference.append(list(data[data[category] == 1]["Reference"]))
            
        flat_list = [item for sublist in reference for item in sublist]
        temp_data = data[data["Reference"].isin(flat_list)]
        
        if (len(selected_reaction) != 0):
            reference = []
            for reaction in selected_reaction:
                reference.append(list(temp_data[temp_data[reaction] >= 1]["Reference"]))
        
        flat_list = [item for sublist in reference for item in sublist]
            
        subset_data = temp_data[temp_data["Reference"].isin(flat_list)]
        subset_data = subset_data.loc[:,["Content", "Comment", "Share", "Angry", "Care", "Haha", "Like", "Love", "Sad", "Wow", "Total Reactions", "Category"]]
        subset_data = subset_data.drop_duplicates().reset_index().drop("index", axis=1)

        subset_data = subset_data.sort_values(by=[selected_sorting], ascending=False)

        
        ROW_DATA = list(subset_data.values.tolist())
        COLUMN_NAMES = subset_data.columns.values
    
        return render_template('explore.html', reaction_type=REACTION_TYPE, category_type=CATEGORY_TYPE, sort_type=SORT_TYPE,
                               row_data=ROW_DATA, column_names=COLUMN_NAMES, zip=zip)
    else:
        
        return render_template("explore.html", reaction_type=REACTION_TYPE, category_type=CATEGORY_TYPE, sort_type=SORT_TYPE)

@app.route("/analysis")
def analysis():
    
    # --------------------------- WORD CLOUD -------------------------------------- #
    add_stop_words = ["just", "really", "year", "many", 
                  "like", "think", "want", "need", "say", "know", "time",
                   "tell", "thing", "say", "make", "come", "ask", "feel", "student"]
    stopwords_list = text.ENGLISH_STOP_WORDS.union(add_stop_words)
    
    full_names = ['Advice', 'Ask Prof Ben', 'Funny', 'Lost and Found', 'Nostalgia', 'Rant', 'Romance']

    def setListOfcolor_func(word=None, font_size=None, position=None, orientation=None, font_path=None, random_state=None):  
        #define the list of set colors  
        color_list = ["#003049", "#d62828", "#F5A700", "#32936f", "#3b0d11"]  
    
        #return a random color in the list  
        return np.random.choice(color_list)  

    def get_wordcloud(text):
        pil_img = WordCloud(stopwords=stopwords_list, font_path='../dashboard/static/font/Gobold Regular.otf', 
                            background_color="white", color_func=setListOfcolor_func,
                            max_words=1000, max_font_size=125, random_state=101).generate(text=text).to_image()
        img = io.BytesIO()
        pil_img.save(img, "PNG")
        img.seek(0)
        img_b64 = base64.b64encode(img.getvalue()).decode()
        return img_b64
    
    class Cloud:
        def __init__(self, category, image):
            self.category = category
            self.image = image
        
    clouds = []
    for cat in full_names:
        cloud = get_wordcloud(data_clean["Spacy_Lemmatize"][cat])
        clouds.append(Cloud(category=cat, image=cloud))
        
    # ----------------------------- RADAR PLOT ----------------------------------- #
    sns.set_style("darkgrid")
        
    def single_make_spider(row, title, color, df, yticks, yticks_label, ylim, my_dpi):
        # number of variable
        categories=list(df)[1:]
        N = len(categories)
    
        # We are going to plot the first line of the data frame.
        # But we need to repeat the first value to close the circular graph:
        values=df.loc[row].drop('Category').values.flatten().tolist()
        values += values[:1]
        values
    
        # What will be the angle of each axis in the plot? (we divide the plot / number of variable)
        angles = [n / float(N) * 2 * pi for n in range(N)]
        angles += angles[:1]
    
        # Initialise the spider plot
        ax = plt.subplot(111, polar=True)
    
        # Draw one axe per variable + add labels
        plt.xticks(angles[:-1], categories, color='grey', size=8)
    
        # Draw ylabels
        ax.set_rlabel_position(0)
        plt.yticks(yticks, yticks_label, color="grey", size=7)
        plt.ylim(0, ylim)
    
        # Plot data
        ax.plot(angles, values, color=color, linewidth=1, linestyle='solid')
    
        # Fill area
        ax.fill(angles, values, color=color, alpha=0.1)
        
        # Add a title
        plt.title(title, size=15, color=color, y=1.1)
    
        plt.tight_layout()
        
        # save file
        img = io.BytesIO()
        plt.savefig(img, format="png")
        img.seek(0)
        
        plot_url = base64.b64encode(img.getvalue()).decode()
        

        return plot_url
        #filename = os.getcwd() + "\\static\\assets\\radar_{}.png".format(row)
        #plt.savefig(filename, dpi=my_dpi, bbox_inches = "tight")
        
    

    # Average Comments, Shares, Reactions
    cat_col = ["Advice", "Ask Prof Ben", "Funny", "Lost and Found", "Nostalgia", "Rant", "Romance"]
    
    comment_list = []
    share_list = []
    reaction_list = []
    
    for cat in cat_col:
        dataframe = data[data[cat] == 1]
        comment_list.append(round(dataframe["Comment"].mean(), 2))
        share_list.append(round(dataframe["Share"].mean(), 2))
        reaction_list.append(round(dataframe["Total Reactions"].mean(), 2))

    df_average = pd.DataFrame(list(zip(cat_col, comment_list, share_list, reaction_list)), columns=["Category", "Comments", "Shares", "Reactions"])
    
    def radar_plot(row):
        # initialize the figure
        my_dpi=200
        plt.figure(figsize=(800/my_dpi, 800/my_dpi), dpi=my_dpi)
         
        # Create a color palette:
        my_palette = plt.cm.get_cmap("Set2", len(df_average.index))
        
        yticks = [20,40,60,80,100,120]
        yticks_label = ["20","40","60","80","100","120"]
        ylim = 120
        
        url = single_make_spider(row=row, title=df_average["Category"][row], color=my_palette(row), df=df_average, 
                        yticks=yticks, yticks_label= yticks_label, ylim=ylim, my_dpi=my_dpi)
        
        return url
    
    list_of_plot_url = []
    row = 0
    for i in range(0, len(df_average)):
       url_name = radar_plot(row)
       list_of_plot_url.append(url_name)
       row += 1

   #--------------------------- BOX PLOT ---------------------------------- #
    advice = data[data["Advice"] == 1]
    askprofben = data[data["Ask Prof Ben"] == 1]
    funny = data[data["Funny"] == 1]
    lostandfound = data[data["Lost and Found"] == 1]
    nostalgia = data[data["Nostalgia"] == 1]
    rant = data[data["Rant"] == 1]
    romance = data[data["Romance"] == 1]
    nocat = data[data["No Category"] == 1]
    
    df1 = advice.loc[:, ["Comment", "Share", "Total Reactions"]]
    df1["Category"] = "Advice"
    
    df2 = askprofben.loc[:, ["Comment", "Share", "Total Reactions"]]
    df2["Category"] = "Ask Prof Ben"
    
    df3 = funny.loc[:, ["Comment", "Share", "Total Reactions"]]
    df3["Category"] = "Funny"
    
    df4 = lostandfound.loc[:, ["Comment", "Share", "Total Reactions"]]
    df4["Category"] = "Lost and Found"
    
    df5 = nostalgia.loc[:, ["Comment", "Share", "Total Reactions"]]
    df5["Category"] = "Nostalgia"
    
    df6 = rant.loc[:, ["Comment", "Share", "Total Reactions"]]
    df6["Category"] = "Rant"
    
    df7 = romance.loc[:, ["Comment", "Share", "Total Reactions"]]
    df7["Category"] = "Romance"
    
    df8 = nocat.loc[:, ["Comment", "Share", "Total Reactions"]]
    df8["Category"] = "No Category"
    
    final_df = df1.append(df2)
    final_df = final_df.append(df3)
    final_df = final_df.append(df4)
    final_df = final_df.append(df5)
    final_df = final_df.append(df6)
    final_df = final_df.append(df7)
    final_df = final_df.append(df8)
    final_df = final_df.reset_index().drop("index", axis=1)
    
    box_plot = pygal.Box(box_mode="tukey", height=400, width=700)
    box_plot.add("Advice", list(final_df[final_df["Category"] == "Advice"]["Comment"]))
    box_plot.add("Ask Prof Ben", list(final_df[final_df["Category"] == "Ask Prof Ben"]["Comment"]))
    box_plot.add("Funny", list(final_df[final_df["Category"] == "Funny"]["Comment"]))
    box_plot.add("Lost and Found", list(final_df[final_df["Category"] == "Lost and Found"]["Comment"]))
    box_plot.add("Nostalgia", list(final_df[final_df["Category"] == "Nostalgia"]["Comment"]))
    box_plot.add("Rant", list(final_df[final_df["Category"] == "Rant"]["Comment"]))
    box_plot.add("Romance", list(final_df[final_df["Category"] == "Romance"]["Comment"]))
    box_plot.add("No Category", list(final_df[final_df["Category"] == "No Category"]["Comment"]))
    box_plot.title = 'Distribution of # comments'
    BOX_PLOT_GRAPH_1 = box_plot.render_data_uri()
    
    box_plot = pygal.Box(box_mode="tukey", height=400, width=700)
    box_plot.add("Advice", list(final_df[final_df["Category"] == "Advice"]["Share"]))
    box_plot.add("Ask Prof Ben", list(final_df[final_df["Category"] == "Ask Prof Ben"]["Share"]))
    box_plot.add("Funny", list(final_df[final_df["Category"] == "Funny"]["Comment"]))
    box_plot.add("Lost and Found", list(final_df[final_df["Category"] == "Lost and Found"]["Share"]))
    box_plot.add("Nostalgia", list(final_df[final_df["Category"] == "Nostalgia"]["Share"]))
    box_plot.add("Rant", list(final_df[final_df["Category"] == "Rant"]["Share"]))
    box_plot.add("Romance", list(final_df[final_df["Category"] == "Romance"]["Share"]))
    box_plot.add("No Category", list(final_df[final_df["Category"] == "No Category"]["Share"]))
    box_plot.title = 'Distribution of # shares'
    BOX_PLOT_GRAPH_2 = box_plot.render_data_uri()
    
    box_plot = pygal.Box(box_mode="tukey", height=400, width=700)
    box_plot.add("Advice", list(final_df[final_df["Category"] == "Advice"]["Total Reactions"]))
    box_plot.add("Ask Prof Ben", list(final_df[final_df["Category"] == "Ask Prof Ben"]["Total Reactions"]))
    box_plot.add("Funny", list(final_df[final_df["Category"] == "Funny"]["Total Reactions"]))
    box_plot.add("Lost and Found", list(final_df[final_df["Category"] == "Lost and Found"]["Total Reactions"]))
    box_plot.add("Nostalgia", list(final_df[final_df["Category"] == "Nostalgia"]["Total Reactions"]))
    box_plot.add("Rant", list(final_df[final_df["Category"] == "Rant"]["Total Reactions"]))
    box_plot.add("Romance", list(final_df[final_df["Category"] == "Romance"]["Total Reactions"]))
    box_plot.add("No Category", list(final_df[final_df["Category"] == "No Category"]["Total Reactions"]))
    box_plot.title = 'Distribution of # reactions'
    BOX_PLOT_GRAPH_3 = box_plot.render_data_uri()

    #------------------------- DOT PLOT ------------------------#
    df1 = advice.loc[:, ["Angry", "Care", "Haha", "Like", "Love", "Sad", "Wow"]]
    df1["Category"] = "Advice"
    
    df2 = askprofben.loc[:, ["Angry", "Care", "Haha", "Like", "Love", "Sad", "Wow"]]
    df2["Category"] = "Ask Prof Ben"
    
    df3 = funny.loc[:, ["Angry", "Care", "Haha", "Like", "Love", "Sad", "Wow"]]
    df3["Category"] = "Funny"
    
    df4 = lostandfound.loc[:, ["Angry", "Care", "Haha", "Like", "Love", "Sad", "Wow"]]
    df4["Category"] = "Lost and Found"
    
    df5 = nostalgia.loc[:, ["Angry", "Care", "Haha", "Like", "Love", "Sad", "Wow"]]
    df5["Category"] = "Nostalgia"
    
    df6 = rant.loc[:, ["Angry", "Care", "Haha", "Like", "Love", "Sad", "Wow"]]
    df6["Category"] = "Rant"
    
    df7 = romance.loc[:, ["Angry", "Care", "Haha", "Like", "Love", "Sad", "Wow"]]
    df7["Category"] = "Romance"
    
    df8 = nocat.loc[:, ["Angry", "Care", "Haha", "Like", "Love", "Sad", "Wow"]]
    df8["Category"] = "No Category"

    final_df = df1.append(df2)
    final_df = final_df.append(df3)
    final_df = final_df.append(df4)
    final_df = final_df.append(df5)
    final_df = final_df.append(df6)
    final_df = final_df.append(df7)
    final_df = final_df.append(df8)
    final_df = final_df.reset_index().drop("index", axis=1)
    
    reaction_category = final_df.groupby("Category")[["Angry", "Care", "Haha", "Like", "Love", "Sad", "Wow"]].sum()
    
    dot_chart = pygal.Dot(x_label_rotation=30, height=500, width=800)
    dot_chart.x_labels = reaction_category.index
    dot_chart.add("Angry", list(reaction_category["Angry"]))
    dot_chart.add("Care", list(reaction_category["Care"]))
    dot_chart.add("Haha", list(reaction_category["Haha"]))
    dot_chart.add("Like", list(reaction_category["Like"]))
    dot_chart.add("Love", list(reaction_category["Love"]))
    dot_chart.add("Sad", list(reaction_category["Sad"]))
    dot_chart.add("Wow", list(reaction_category["Wow"]))
    dot_chart.title = '# of reactions in each category'
    DOT_PLOT_GRAPH_4 = dot_chart.render_data_uri()
    
    #------------------------- HISTOGRAM ---------------------------#
    fig = px.histogram(data, x="Comment", marginal="rug", title="Distribution of Number of Comments")
    div1 = fig.to_html(full_html=False)
   
    fig = px.histogram(data, x="Share", marginal="rug", title="Distribution of Number of Shares")
    div2 = fig.to_html(full_html=False)
    
    fig = px.histogram(data, x="Total Reactions", marginal="rug", title="Distribution of Number of Reactions")
    div3 = fig.to_html(full_html=False)
   

    return render_template('analysis.html', articles=clouds, plots=list_of_plot_url, 
                           box_plot_graph_1 = BOX_PLOT_GRAPH_1,
                           box_plot_graph_2 = BOX_PLOT_GRAPH_2,
                           box_plot_graph_3 = BOX_PLOT_GRAPH_3,
                           dot_plot_graph_4 = DOT_PLOT_GRAPH_4,
                           hist_comments = div1,
                           hist_shares = div2,
                           hist_reactions = div3)

   
if __name__ == "__main__":
    app.run(debug=False)