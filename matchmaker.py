import pandas as pd
from collections import defaultdict

class MatchingAlgorithm:
    def __init__(self, mentee_file: str, mentor_file: str):
        # Load mentee and mentor CSV files
        self.mentees = pd.read_csv(mentee_file)
        self.mentors = pd.read_csv(mentor_file)
        
        # Initialize empty matches and preferences
        self.matches = {}

    def preprocess_data(self):
        # Ensure compatibility and consistency in data types
        for col in ['Experience', 'Field', 'CareerStage', 'Studies', 'Objectives', 'Capacities', 'Name']:
            if col in self.mentees.columns:
                self.mentees[col] = self.mentees[col].astype(str).str.lower()
            if col in self.mentors.columns:
                self.mentors[col] = self.mentors[col].astype(str).str.lower()

    def generate_preferences(self):
        mentee_preferences = {}
        mentor_preferences = defaultdict(list)

        # Create preferences based on given criteria
        for mentee_index, mentee in self.mentees.iterrows():
            preferences = []
            for mentor_index, mentor in self.mentors.iterrows():
                # Evaluate matching criteria
                score = 0
                
                # Matching criteria weights can be adjusted as necessary
                if mentee['Experience'] == mentor['Experience']:
                    score += 2
                if mentee['Field'] == mentor['Field']:
                    score += 2
                if mentee['CareerStage'] < mentor['CareerStage']:  # Mentee earlier career stage
                    score += 3
                if mentee['Studies'] < mentor['Studies']:  # Mentor more advanced studies
                    score += 1
                if mentee['Objectives'] in mentor['Capacities']:
                    score += 3

                preferences.append((mentor_index, score))
            
            # Sort by score descending to create preferences
            mentee_preferences[mentee_index] = [mentor for mentor, _ in sorted(preferences, key=lambda x: -x[1])]

        # Reverse mentor preferences for better algorithm alignment
        for mentor_index, mentor in self.mentors.iterrows():
            preferences = []
            for mentee_index, mentee in self.mentees.iterrows():
                if mentee_index in mentee_preferences:
                    preferences.append((mentee_index, mentee_preferences[mentee_index].index(mentor_index)))
            mentor_preferences[mentor_index] = [mentee for mentee, _ in sorted(preferences, key=lambda x: x[1])]

        return mentee_preferences, mentor_preferences

    def gale_shapley_matching(self, mentee_preferences, mentor_preferences):
        # Gale-Shapley matching algorithm
        mentees_free = set(mentee_preferences.keys())
        mentor_engagements = {mentor_index: None for mentor_index in mentor_preferences.keys()}
        mentee_proposals = defaultdict(int)

        while mentees_free:
            mentee_index = mentees_free.pop()
            preferred_mentors = mentee_preferences[mentee_index]

            # Propose to the next mentor on mentee's list
            if mentee_proposals[mentee_index] < len(preferred_mentors):
                mentor_index = preferred_mentors[mentee_proposals[mentee_index]]
                mentee_proposals[mentee_index] += 1

                current_mentee = mentor_engagements[mentor_index]
                
                # Engage if no current mentee or mentee has better ranking
                if current_mentee is None or mentor_preferences[mentor_index].index(mentee_index) < mentor_preferences[mentor_index].index(current_mentee):
                    mentor_engagements[mentor_index] = mentee_index
                    
                    if current_mentee is not None:
                        mentees_free.add(current_mentee)  # Previous mentee is now free
                else:
                    mentees_free.add(mentee_index)  # Mentee stays free if rejected

        self.matches = {mentor_index: mentee_index for mentor_index, mentee_index in mentor_engagements.items() if mentee_index is not None}

    def run_matching(self):
        self.preprocess_data()
        mentee_preferences, mentor_preferences = self.generate_preferences()
        self.gale_shapley_matching(mentee_preferences, mentor_preferences)

    def display_matches(self):
        print("Final Matches:")
        for mentor, mentee in self.matches.items():
            mentor_name = self.mentors.loc[mentor, 'Name'].capitalize() if 'Name' in self.mentors.columns else f"Mentor {mentor}"
            mentee_name = self.mentees.loc[mentee, 'Name'].capitalize() if 'Name' in self.mentees.columns else f"Mentee {mentee}"
            print(f"Mentor: {mentor_name} <--> Mentee: {mentee_name}")


# Usage Example
algorithm = MatchingAlgorithm("mentees.csv", "mentors.csv")
algorithm.run_matching()
algorithm.display_matches()
