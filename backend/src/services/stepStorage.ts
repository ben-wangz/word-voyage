import { Step } from '../types/index.ts';

/**
 * Step Storage Service
 * Manage Step persistence (use memory in MVP phase, switch to Redis later)
 */
export class StepStorageService {
  private steps: Map<string, Step> = new Map();

  /**
   * Save Step
   */
  async saveStep(step: Step): Promise<void> {
    this.steps.set(step.id, step);
    console.log(`Step saved: ${step.id}`);
  }

  /**
   * Get Step
   */
  async getStep(stepId: string): Promise<Step | null> {
    return this.steps.get(stepId) || null;
  }

  /**
   * Get multiple Steps
   */
  async getSteps(stepIds: string[]): Promise<Step[]> {
    const steps: Step[] = [];
    for (const id of stepIds) {
      const step = this.steps.get(id);
      if (step) {
        steps.push(step);
      }
    }
    return steps;
  }

  /**
   * Delete Step
   */
  async deleteStep(stepId: string): Promise<void> {
    this.steps.delete(stepId);
  }

  /**
   * Get the latest N Steps (based on session)
   */
  async getRecentSteps(stepIds: string[], limit: number): Promise<Step[]> {
    const steps = await this.getSteps(stepIds);
    return steps.slice(-limit);
  }
}

// Global singleton
let storageInstance: StepStorageService | null = null;

export function initStepStorage(): StepStorageService {
  storageInstance = new StepStorageService();
  return storageInstance;
}

export function getStepStorage(): StepStorageService {
  if (!storageInstance) {
    throw new Error('Step storage not initialized. Call initStepStorage first.');
  }
  return storageInstance;
}
