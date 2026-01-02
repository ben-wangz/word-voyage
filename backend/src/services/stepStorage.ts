import { Step } from '../types/index.ts';
import type { IStorageAdapter } from './storage/index.ts';
import { config } from '../config.ts';

export class StepStorageService {
  private storage: IStorageAdapter;

  constructor(storage: IStorageAdapter) {
    this.storage = storage;
  }

  async saveStep(step: Step): Promise<void> {
    await this.storage.set(`step:${step.id}`, JSON.stringify(step), config.ttl.step);
    console.log(`Step saved: ${step.id}`);
  }

  async getStep(stepId: string): Promise<Step | null> {
    const data = await this.storage.get(`step:${stepId}`);
    if (!data) return null;
    return JSON.parse(data);
  }

  async getSteps(stepIds: string[]): Promise<Step[]> {
    if (stepIds.length === 0) return [];

    const keys = stepIds.map((id) => `step:${id}`);
    const results = await this.storage.mget(keys);

    const steps: Step[] = [];
    for (const data of results) {
      if (data) {
        steps.push(JSON.parse(data));
      }
    }
    return steps;
  }

  async deleteStep(stepId: string): Promise<void> {
    await this.storage.delete(`step:${stepId}`);
  }

  async getRecentSteps(stepIds: string[], limit: number): Promise<Step[]> {
    const steps = await this.getSteps(stepIds);
    return steps.slice(-limit);
  }
}

let storageInstance: StepStorageService | null = null;

export function initStepStorage(storage: IStorageAdapter): StepStorageService {
  storageInstance = new StepStorageService(storage);
  return storageInstance;
}

export function getStepStorage(): StepStorageService {
  if (!storageInstance) {
    throw new Error('Step storage not initialized. Call initStepStorage first.');
  }
  return storageInstance;
}
