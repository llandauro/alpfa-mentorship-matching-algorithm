import pandas as pd
from collections import defaultdict

class MatchingAlgorithm:
    def __init__(self, mentee_file: str, mentor_file: str):
        self.mentees = pd.read_csv(mentee_file)
        self.mentors = pd.read_csv(mentor_file)
        self.matches = {}

    def preprocess_data(self):
        # Ensure compatibility and consistency in data types
        cols = ['Experience', 'Field', 'CareerStage', 'Studies', 'Objectives', 'Capacities', 'Name']
        for col in cols:
            if col in self.mentees.columns:
                self.mentees[col] = self.mentees[col].astype(str).str.lower()
            if col in self.mentors.columns:
                self.mentors[col] = self.mentors[col].astype(str).str.lower()

    def generate_preferences(self):
        mentee_preferences = {}
        mentor_preferences = defaultdict(list)
        
        # 1. Define Mappings for comparison
        stage_map = {'entry level': 1, 'mid level': 2, 'senior level': 3}
        studies_map = {'bachelor': 1, 'master': 2, 'phd': 3}
        
        # Dictionary to store compatibility scores for both sides to use
        compatibility_scores = {}

        for mentee_idx, mentee in self.mentees.iterrows():
            for mentor_idx, mentor in self.mentors.iterrows():
                score = 0
                
                # 2. Experience Logic: Mentor should have MORE experience, not equal
                try:
                    mentee_exp = int(mentee['Experience'].split()[0])
                    mentor_exp = int(mentor['Experience'].split()[0])
                    if mentor_exp > mentee_exp:
                        score += 2
                        score += (mentee_exp * 0.1)
                except (ValueError, IndexError):
                    pass # Handle cases like "n/a" safely

                # Field Match
                if mentee['Field'] == mentor['Field']:
                    score += 2
                
                # 3. Ordinal Logic: Use maps 
                if stage_map.get(mentee['CareerStage'], 0) < stage_map.get(mentor['CareerStage'], 0):
                    score += 3
                if studies_map.get(mentee['Studies'], 0) < studies_map.get(mentor['Studies'], 0):
                    score += 1
                
                # Objectives
                if mentee['Objectives'] in mentor['Capacities']:
                    score += 3

                # Store score for this pair
                compatibility_scores[(mentee_idx, mentor_idx)] = score

        # 4. Generate Sorted Preference Lists for BOTH sides based on the Score
        for mentee_idx in self.mentees.index:
            # Sort all mentors by score (descending)
            ranked_mentors = sorted(self.mentors.index, key=lambda m_idx: -compatibility_scores[(mentee_idx, m_idx)])
            mentee_preferences[mentee_idx] = ranked_mentors

        for mentor_idx in self.mentors.index:
            # Sort all mentees by score (descending)
            ranked_mentees = sorted(self.mentees.index, key=lambda m_idx: -compatibility_scores[(m_idx, mentor_idx)])
            mentor_preferences[mentor_idx] = ranked_mentees

        return mentee_preferences, mentor_preferences

    def gale_shapley_matching(self, mentee_preferences, mentor_preferences):
        mentees_free = list(mentee_preferences.keys()) # Use list for stable ordering
        mentor_engagements = {mentor_index: None for mentor_index in mentor_preferences.keys()}
        mentee_proposals = defaultdict(int)

        while mentees_free:
            mentee_index = mentees_free.pop(0) # Pop from front
            preferred_mentors = mentee_preferences[mentee_index]

            if mentee_proposals[mentee_index] < len(preferred_mentors):
                mentor_index = preferred_mentors[mentee_proposals[mentee_index]]
                mentee_proposals[mentee_index] += 1

                current_mentee = mentor_engagements[mentor_index]
                
                # Check if mentor is free OR prefers the new mentee
                # Note: .index() is safe here because lists are complete
                if current_mentee is None or mentor_preferences[mentor_index].index(mentee_index) < mentor_preferences[mentor_index].index(current_mentee):
                    mentor_engagements[mentor_index] = mentee_index
                    
                    if current_mentee is not None:
                        mentees_free.append(current_mentee) # Previous mentee is free again
                else:
                    mentees_free.append(mentee_index) # Mentee rejected, back to queue

        self.matches = {mentor_index: mentee_index for mentor_index, mentee_index in mentor_engagements.items() if mentee_index is not None}

    def run_matching(self):
        self.preprocess_data()
        mentee_preferences, mentor_preferences = self.generate_preferences()
        self.gale_shapley_matching(mentee_preferences, mentor_preferences)

    def display_matches(self):
        print("Final Matches:")
        for mentor, mentee in self.matches.items():
            mentor_name = self.mentors.loc[mentor, 'Name'].capitalize()
            mentee_name = self.mentees.loc[mentee, 'Name'].capitalize()
            print(f"Mentor: {mentor_name} <--> Mentee: {mentee_name}")

# Usage
algorithm = MatchingAlgorithm("mentees.csv", "mentors.csv")
algorithm.run_matching()
algorithm.display_matches()