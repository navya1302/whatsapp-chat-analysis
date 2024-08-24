
import streamlit as st
import helper
import preprocessor
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import pandas as pd
from collections import Counter


st.sidebar.title("Whatsapp Chat Analyser")

uploaded_file=st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data=uploaded_file.getvalue()
    data=bytes_data.decode("utf-8")

    df=preprocessor.preprocess(data)

    st.dataframe(df)

    user_list=df['user'].unique().tolist()
    user_list.sort()
    user_list.insert(0,'overall')

    selected_user=st.sidebar.selectbox('Show analysis wrt',user_list)
    if selected_user!='overall':
        new_df = df[df['user'] == selected_user]
    else:
        new_df=df

    if st.sidebar.button("Show Analysis"):


        col1,col2,col3,col4=st.columns(4)


        with col1:
            st.header("Total messages")

            if selected_user == 'overall':
                num_messages=df.shape[0]
            else:
               num_messages=new_df.shape[0]
            st.title(num_messages)


        with col2:
            st.header("Total media")
            if selected_user == 'overall':
                filtered_df = df[df['message'].str.contains('video omitted|image omitted', case=False, na=False)]
                media=filtered_df.shape[0]
            else:
                filtered_df = df[(df['user'] == selected_user) &
                                 (df['message'].str.contains('video omitted|image omitted', case=False, na=False))]
                media=filtered_df.shape[0]
            st.title(media)

        with col3:
            from urlextract import URLExtract
            extractor=URLExtract()

            st.header('Total Links')

            def links(df):
                links_list=[]

                for mssg in df['message']:
                    links_list.extend(extractor.find_urls(mssg))

                return len(links_list)

            if selected_user=='overall':
                link=links(df)
            else:
                link=links(new_df)

            st.title(link)

        if selected_user=='overall':

            st.title("Most Busy Users")
            x=df['user'].value_counts().head()

            fig,ax=plt.subplots()


            col1, col2 = st.columns(2)

            with col1:
                ax.bar(x.index, x.values)
                st.pyplot(fig)
                plt.xticks(rotation='vertical')


            x2=round((df['user'].value_counts())/df.shape[0]*100,2).reset_index().rename(columns={'index':'name','user':'percent'})

            with col2:
                st.dataframe(x2)


            def create_wordcloud(selected_user, df):
                if selected_user != 'overall':
                    df = df[df['user'] == selected_user]

                wc = WordCloud(width=500, height=500, min_font_size=10, background_color='black')

                # Generate word cloud only for the selected user's messages
                df_wc = wc.generate(df['message'].str.cat(sep=" "))
                return df_wc


            # Assume `selected_user` and `df` are already defined in your Streamlit app
            if selected_user!='overall':
                df_wc = create_wordcloud(selected_user,df)

                fig, ax = plt.subplots()
                ax.imshow(df_wc, interpolation='bilinear')
                ax.axis('off')  # Hide axes

                # Display the word cloud in Streamlit
                st.pyplot(fig)


            #most common words

            def common_words(selected_user, df):
                # Exclude media messages
                temp = df[
                    ~df['message'].str.contains('video omitted\n|image omitted\n|video omitted|image omitted|omitted',
                                                case=False, na=False)
                ]

                # Load stop words
                f = open('stop_hinglish.txt', 'r')
                stop_words = f.read().splitlines()

                f = open('hindi_stop_words.txt', encoding='utf-8')
                hindi = f.read().splitlines()

                words = []

                # Split and filter words
                for message in temp['message']:
                    for word in message.lower().split():
                        if word not in stop_words and word not in hindi:
                            words.append(word)

                return pd.DataFrame(Counter(words).most_common(20), columns=['Word', 'Count'])


            # Use the correct DataFrame for the selected user
            if selected_user == 'overall':
                most_common_df = common_words(selected_user, df)
            else:
                new_df = df[df['user'] == selected_user]
                most_common_df = common_words(selected_user, new_df)  # Pass new_df instead of df

            # Display the DataFrame

            # most_common_df=pd.DataFrame(most_common_df,columns=['word','count'])
            # st.dataframe(most_common_df)

            fig,ax=plt.subplots()

            ax.barh(most_common_df['Word'],most_common_df['Count'])
            plt.xticks(rotation='vertical')
            st.title("Most Common Words")

            st.pyplot(fig)












