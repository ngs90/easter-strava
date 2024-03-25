# Strava Activities Dashboard

## Overview
This project presents a comprehensive Streamlit dashboard for Strava activities. It's designed to load data from Strava, store it in a Neo4j database, and then provide insightful statistics about these activities. Additionally, a chatbot is integrated to answer questions regarding the Strava activities, making it a versatile tool for athletes and fitness enthusiasts who wish to track and analyze their performance over time.

## Features
- **Strava Data Loader**: Fetches activities from Strava and loads them into a Neo4j database, ensuring that your activity data is structured and ready for analysis.
- **Neo4j Database Integration**: Utilizes the powerful features of Neo4j to store and manage Strava activities, enabling complex queries and relationships between different data points.
- **Activity Statistics**: A dedicated tab within the application that aggregates and displays statistics about your Strava activities, offering insights into performance trends, activity types, and more.
- **Chatbot for Queries**: An AI-powered chatbot that provides answers to various questions about your Strava activities, from simple queries about individual activities to complex questions regarding performance trends.

## Getting Started
To get started with this project, you'll need to install the required dependencies, set up your environment variables, and configure access to both Strava and Neo4j.

### Prerequisites
- Python 3.7+
- Neo4j Database
- Strava API Access
- OpenAI API Access

### Installation
1. Clone the repository to your local machine.
2. Install the required dependencies using `pip install -r requirements.txt`.
3. Configure your environment variables for Neo4j and Strava API access (refer to `src/config.py` for the required variables). The project will assume that the environmental variables are defined in the file `src/.env` (has to be created) and loaded using the dotenv-package
4. Run the Streamlit application using `streamlit run src/main.py`.

## How to Use
- **Loading Data**: Initially, load your Strava activities into the Neo4j database using the provided interface.
- **Viewing Statistics**: Navigate to the statistics tab to see detailed analytics about your activities.
- **Chatbot Interaction**: Use the chat tab to ask questions and get insights directly from the chatbot.

## Future Enhancements
- **Activity Comparison**: Implement features for comparing activities over time or against activities of friends.
- **Goal Tracking**: Add functionality to set and track goals related to distance, speed, or calories burned.
- **Social Features**: Integrate social features that allow users to share their achievements or compare performances with a broader community.
- **Advanced Analytics**: Incorporate machine learning models to provide advanced predictions about future performances or suggest training optimizations.

## Contributions
Contributions are welcome! If you have suggestions or want to improve the application, feel free to create a pull request or open an issue.
