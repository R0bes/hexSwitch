import { useState, useCallback, useRef } from 'react';
import type { ScenarioReport, ScenarioMetrics, StepMetrics, ReportLog, ReportTrace, ReportError } from '../types/report';

interface UseScenarioReportOptions {
  scenarioId: string;
  scenarioName: string;
  totalSteps: number;
}

export function useScenarioReport({ scenarioId, scenarioName, totalSteps }: UseScenarioReportOptions) {
  const [report, setReport] = useState<ScenarioReport | null>(null);
  const [isCollecting, setIsCollecting] = useState(false);
  
  const startTimeRef = useRef<number>(0);
  const stepMetricsRef = useRef<Map<string, StepMetrics>>(new Map());
  const logsRef = useRef<ReportLog[]>([]);
  const tracesRef = useRef<ReportTrace[]>([]);
  const errorsRef = useRef<ReportError[]>([]);

  const startCollection = useCallback(() => {
    setIsCollecting(true);
    startTimeRef.current = Date.now();
    stepMetricsRef.current.clear();
    logsRef.current = [];
    tracesRef.current = [];
    errorsRef.current = [];
  }, []);

  const recordStepStart = useCallback((stepId: string, stepName: string) => {
    if (!isCollecting) return;
    
    stepMetricsRef.current.set(stepId, {
      stepId,
      stepName,
      startTime: Date.now(),
      endTime: 0,
      duration: 0,
      status: 'running'
    });
  }, [isCollecting]);

  const recordStepEnd = useCallback((stepId: string, status: 'success' | 'error') => {
    if (!isCollecting) return;
    
    const stepMetric = stepMetricsRef.current.get(stepId);
    if (stepMetric) {
      stepMetric.endTime = Date.now();
      stepMetric.duration = stepMetric.endTime - stepMetric.startTime;
      stepMetric.status = status;
    }
  }, [isCollecting]);

  const recordLog = useCallback((log: Omit<ReportLog, 'timestamp'>) => {
    if (!isCollecting) return;
    
    logsRef.current.push({
      ...log,
      timestamp: new Date().toISOString()
    });
  }, [isCollecting]);

  const recordTrace = useCallback((trace: Omit<ReportTrace, 'id' | 'startTime' | 'endTime' | 'duration'>) => {
    if (!isCollecting) return;
    
    const startTime = Date.now();
    const endTime = startTime + (trace.spans.reduce((sum, span) => sum + span.duration, 0));
    
    tracesRef.current.push({
      ...trace,
      id: `trace-${tracesRef.current.length + 1}`,
      startTime,
      endTime,
      duration: endTime - startTime
    });
  }, [isCollecting]);

  const recordError = useCallback((error: Omit<ReportError, 'id' | 'timestamp'>) => {
    if (!isCollecting) return;
    
    errorsRef.current.push({
      ...error,
      id: `error-${errorsRef.current.length + 1}`,
      timestamp: Date.now()
    });
  }, [isCollecting]);

  const generateReport = useCallback((completedSteps: number, failedSteps: number) => {
    if (!isCollecting || startTimeRef.current === 0) return null;

    const endTime = Date.now();
    const duration = endTime - startTimeRef.current;
    const stepMetrics = Array.from(stepMetricsRef.current.values());
    const averageStepDuration = stepMetrics.length > 0
      ? stepMetrics.reduce((sum, step) => sum + step.duration, 0) / stepMetrics.length
      : 0;
    const throughput = duration > 0 ? (completedSteps / (duration / 1000)) : 0;

    const metrics: ScenarioMetrics = {
      startTime: startTimeRef.current,
      endTime,
      duration,
      totalSteps,
      completedSteps,
      failedSteps,
      averageStepDuration,
      throughput
    };

    const finalReport: ScenarioReport = {
      scenarioId,
      scenarioName,
      metrics,
      stepMetrics,
      logs: logsRef.current,
      traces: tracesRef.current,
      errors: errorsRef.current,
      generatedAt: Date.now()
    };

    setReport(finalReport);
    setIsCollecting(false);
    return finalReport;
  }, [isCollecting, scenarioId, scenarioName, totalSteps]);

  const clearReport = useCallback(() => {
    setReport(null);
    startTimeRef.current = 0;
    stepMetricsRef.current.clear();
    logsRef.current = [];
    tracesRef.current = [];
    errorsRef.current = [];
  }, []);

  return {
    report,
    isCollecting,
    startCollection,
    recordStepStart,
    recordStepEnd,
    recordLog,
    recordTrace,
    recordError,
    generateReport,
    clearReport
  };
}

