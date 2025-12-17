export interface ScenarioMetrics {
  startTime: number;
  endTime: number;
  duration: number;
  totalSteps: number;
  completedSteps: number;
  failedSteps: number;
  averageStepDuration: number;
  throughput: number; // Steps per second
}

export interface StepMetrics {
  stepId: string;
  stepName: string;
  startTime: number;
  endTime: number;
  duration: number;
  status: 'success' | 'error' | 'running' | 'pending';
}

export interface ReportLog {
  timestamp: string;
  level: 'INFO' | 'WARN' | 'ERROR' | 'DEBUG';
  source: string;
  message: string;
  target?: string;
  stepId?: string;
}

export interface ReportTrace {
  id: string;
  name: string;
  startTime: number;
  endTime: number;
  duration: number;
  spans: Array<{
    name: string;
    startTime: number;
    endTime: number;
    duration: number;
  }>;
}

export interface ReportError {
  id: string;
  timestamp: number;
  stepId: string;
  stepName: string;
  message: string;
  source: string;
  stack?: string;
}

export interface ScenarioReport {
  scenarioId: string;
  scenarioName: string;
  metrics: ScenarioMetrics;
  stepMetrics: StepMetrics[];
  logs: ReportLog[];
  traces: ReportTrace[];
  errors: ReportError[];
  generatedAt: number;
}


