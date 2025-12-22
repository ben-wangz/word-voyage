import { Hono } from 'hono';
import { ProcessingChain } from '../core/processingChain.ts';
import { InputProcessingNode } from '../nodes/inputProcessingNode.ts';
import { TimeManagementNode } from '../nodes/timeManagementNode.ts';
import { StateManagementNode } from '../nodes/stateManagementNode.ts';
import { PreLogSummaryNode } from '../nodes/preLogSummaryNode.ts';
import { LLMCoreNode } from '../nodes/llmCoreNode.ts';
import { getSession } from '../services/session.ts';
import { getStepStorage } from '../services/stepStorage.ts';
import type { Context, ContextField, Step, ProcessStepRequest, StartGameRequest } from '../types/index.ts';

const gameRouter = new Hono();

/**
 * Initialize processing chain
 */
function createProcessingChain(): ProcessingChain {
  const chain = new ProcessingChain();

  // Preprocessing stage
  chain.register(new InputProcessingNode());
  chain.register(new TimeManagementNode());
  chain.register(new StateManagementNode());
  chain.register(new PreLogSummaryNode());

  // Event generation stage
  chain.register(new LLMCoreNode());

  return chain;
}

/**
 * Create initial Context
 */
function createInitialContext(): Context {
  return {
    state: {
      health: { value: 100, type: 'number', description: 'Health points' },
      hunger: { value: 50, type: 'number', description: 'Hunger level' },
      thirst: { value: 50, type: 'number', description: 'Thirst level' },
      energy: { value: 80, type: 'number', description: 'Energy level' },
      location: { value: 'Crashed Spaceship', type: 'string', description: 'Current location' },
    },
    gameTime: 0,
  };
}

/**
 * POST /api/game/start - Start a new game
 */
gameRouter.post('/start', async (c) => {
  try {
    const sessionService = getSession();
    const storage = getStepStorage();

    // Create new session
    const session = sessionService.createSession();

    // Create initial context
    const initialContext = createInitialContext();

    // Create initial step
    const initialStep: Step = {
      id: crypto.randomUUID(),
      timestamp: Date.now(),
      userInput: '[GAME_START]',
      inputType: 'action',
      context: initialContext,
      event: {
        description:
          'Your spacecraft crashes during an emergency landing on an unknown planet. Alarms blare inside the cabin, and oxygen levels are dropping. You must find a way to survive and escape this desolate world.',
        contextChanges: {},
      },
      preLogSummary: {
        summary: 'Game starts. Player awakens in a crashed spaceship.',
        recentEvents: [],
        generatedAt: Date.now(),
      },
    };

    // Save initial step
    await storage.saveStep(initialStep);

    // Update session
    sessionService.updateCurrentStep(session.sessionId, initialStep.id);

    return c.json({
      step: initialStep,
      sessionId: session.sessionId,
    });
  } catch (error: any) {
    console.error('Error starting game:', error);
    return c.json({ error: { code: 'INTERNAL_ERROR', message: error.message } }, 500);
  }
});

/**
 * POST /api/game/step - Process user input
 */
gameRouter.post('/step', async (c) => {
  try {
    const body = await c.req.json<ProcessStepRequest>();
    const { input, sessionId } = body;

    if (!input) {
      return c.json({ error: { code: 'INVALID_INPUT', message: 'Input is required' } }, 400);
    }

    if (!sessionId) {
      return c.json({ error: { code: 'INVALID_SESSION', message: 'Session ID is required' } }, 400);
    }

    const sessionService = getSession();
    const storage = getStepStorage();

    // Get session
    const session = sessionService.getSession(sessionId);
    if (!session) {
      return c.json({ error: { code: 'SESSION_NOT_FOUND', message: 'Session not found' } }, 404);
    }

    // Load current context from last step
    let currentContext: Context;
    if (session.currentStepId) {
      const lastStep = await storage.getStep(session.currentStepId);
      if (lastStep) {
        currentContext = JSON.parse(JSON.stringify(lastStep.context));
      } else {
        currentContext = createInitialContext();
      }
    } else {
      currentContext = createInitialContext();
    }

    // Create processing chain
    const chain = createProcessingChain();

    // Prepare request object
    const request = { input };

    // Execute processing chain
    await chain.execute(request, currentContext);

    // Extract results from request
    const req = request as any;
    const newStep: Step = {
      id: crypto.randomUUID(),
      timestamp: Date.now(),
      userInput: req.userInput,
      inputType: req.inputType,
      context: currentContext,
      event: req.event,
      preLogSummary: req.preLogSummary,
    };

    // Save new step
    await storage.saveStep(newStep);

    // Update session
    sessionService.updateCurrentStep(sessionId, newStep.id);

    return c.json({
      step: newStep,
      sessionId,
    });
  } catch (error: any) {
    console.error('Error processing step:', error);
    return c.json({ error: { code: 'INTERNAL_ERROR', message: error.message } }, 500);
  }
});

/**
 * GET /api/game/context/:sessionId - Get current context
 */
gameRouter.get('/context/:sessionId', async (c) => {
  try {
    const sessionId = c.req.param('sessionId');

    const sessionService = getSession();
    const storage = getStepStorage();

    const session = sessionService.getSession(sessionId);
    if (!session) {
      return c.json({ error: { code: 'SESSION_NOT_FOUND', message: 'Session not found' } }, 404);
    }

    if (!session.currentStepId) {
      return c.json({ context: createInitialContext() });
    }

    const currentStep = await storage.getStep(session.currentStepId);
    if (!currentStep) {
      return c.json({ context: createInitialContext() });
    }

    return c.json({ context: currentStep.context });
  } catch (error: any) {
    console.error('Error getting context:', error);
    return c.json({ error: { code: 'INTERNAL_ERROR', message: error.message } }, 500);
  }
});

/**
 * GET /api/game/history/:sessionId - Get step history
 */
gameRouter.get('/history/:sessionId', async (c) => {
  try {
    const sessionId = c.req.param('sessionId');

    const sessionService = getSession();
    const storage = getStepStorage();

    const session = sessionService.getSession(sessionId);
    if (!session) {
      return c.json({ error: { code: 'SESSION_NOT_FOUND', message: 'Session not found' } }, 404);
    }

    const stepIds = sessionService.getStepHistory(sessionId);
    const steps = await storage.getSteps(stepIds);

    return c.json({ steps });
  } catch (error: any) {
    console.error('Error getting history:', error);
    return c.json({ error: { code: 'INTERNAL_ERROR', message: error.message } }, 500);
  }
});

export default gameRouter;
