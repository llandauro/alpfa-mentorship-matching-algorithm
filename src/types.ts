export interface Participant {
  Name: string;
  Experience: string;
  Field: string;
  CareerStage: string;
  Studies: string;
  Objectives?: string; // Optional for mentors
  Capacities?: string; // Optional for mentees
}

export interface MatchSettings {
  experienceWeight: number;
  fieldWeight: number;
  stageWeight: number;
}

export interface MatchResponse {
  matches: { [mentorIndex: string]: number };
}