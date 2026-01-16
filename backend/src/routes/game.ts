import { Hono } from 'hono';
import { ProcessingChain } from '../core/processingChain.ts';
import { InputProcessingNode } from '../nodes/inputProcessingNode.ts';
import { TimeManagementNode } from '../nodes/timeManagementNode.ts';
import { StateManagementNode } from '../nodes/stateManagementNode.ts';
import { PreLogSummaryNode } from '../nodes/preLogSummaryNode.ts';
import { LLMCoreNode } from '../nodes/llmCoreNode.ts';
import { getSession } from '../services/session.ts';
import { getStepStorage } from '../services/stepStorage.ts';
import type { Context, Step, ProcessStepRequest, I18nContext } from '../types/index.ts';

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
function createInitialContext(t: (key: string, defaultValue?: string) => string): Context {
  return {
    state: {
      health: {
        value: 100,
        type: 'int',
        name: t('game:initial.state.health.name', 'Health'),
        description: t('game:initial.state.health.description', "Character's health points, death at 0"),
        min: 0,
        max: 100,
      },
      hunger: {
        value: 50,
        type: 'int',
        name: t('game:initial.state.hunger.name', 'Hunger'),
        description: t('game:initial.state.hunger.description', 'Hunger level, affects health when too high'),
        min: 0,
        max: 100,
      },
      thirst: {
        value: 50,
        type: 'int',
        name: t('game:initial.state.thirst.name', 'Thirst'),
        description: t('game:initial.state.thirst.description', 'Thirst level, affects health when too high'),
        min: 0,
        max: 100,
      },
      energy: {
        value: 80,
        type: 'int',
        name: t('game:initial.state.energy.name', 'Energy'),
        description: t('game:initial.state.energy.description', 'Energy level, affects action capability'),
        min: 0,
        max: 100,
      },
      location: {
        value: t('game:initial.state.location.value', 'Crashed Spaceship'),
        type: 'string',
        name: t('game:initial.state.location.name', 'Location'),
        description: t('game:initial.state.location.description', 'Current location in the game world'),
      },
    },
    gameTime: 0,
  };
}

/**
 * POST /api/game/start - Start a new game
 */
gameRouter.post('/start', async (c) => {
  try {
    const t = c.get('t') as I18nContext['t'];
    const sessionId = c.get('sessionId') as string;
    const sessionService = getSession();
    const storage = getStepStorage();

    const session = await sessionService.getSession(sessionId);
    if (!session) {
      return c.json({ error: { code: 'SESSION_NOT_FOUND', message: t('common:errors.sessionNotFound', 'Session not found') } }, 404);
    }

    const initialContext = createInitialContext(t);

    const initialStep: Step = {
      id: crypto.randomUUID(),
      timestamp: Date.now(),
      userInput: '[GAME_START]',
      inputType: 'action',
      context: initialContext,
      event: {
        description: t(
          'game:initial.eventDescription',
          'Your spacecraft crashes during an emergency landing on an unknown planet. Alarms blare inside the cabin, and oxygen levels are dropping. You must find a way to survive and escape this desolate world.',
        ),
        contextChanges: {},
      },
      preLogSummary: {
        summary: t('game:initial.summary', 'Game starts. Player awakens in a crashed spaceship.'),
        recentEvents: [],
        generatedAt: Date.now(),
      },
    };

    await storage.saveStep(initialStep);
    await sessionService.updateCurrentStep(sessionId, initialStep.id);

    return c.json({
      step: initialStep,
      sessionId,
    });
  } catch (error: any) {
    console.error('Error starting game:', error);
    const t = c.get('t') as I18nContext['t'];
    return c.json({ error: { code: 'INTERNAL_ERROR', message: t('common:errors.internalError', error.message) } }, 500);
  }
});

/**
 * POST /api/game/step - Process user input
 */
gameRouter.post('/step', async (c) => {
  try {
    const t = c.get('t') as I18nContext['t'];
    const body = await c.req.json<ProcessStepRequest>();
    const { input } = body;

    if (!input) {
      return c.json({ error: { code: 'INVALID_INPUT', message: t('common:errors.inputRequired', 'Input is required') } }, 400);
    }

    const sessionId = c.get('sessionId') as string;
    const userId = c.get('userId') as string;
    const sessionService = getSession();
    const storage = getStepStorage();

    const session = await sessionService.getSession(sessionId);
    if (!session) {
      return c.json({ error: { code: 'SESSION_NOT_FOUND', message: t('common:errors.sessionNotFound', 'Session not found') } }, 404);
    }

    if (session.userId !== userId) {
      return c.json({ error: { code: 'FORBIDDEN', message: t('common:errors.forbidden', 'Access denied') } }, 403);
    }

    // Load current context from last step
    let currentContext: Context;
    if (session.currentStepId) {
      const lastStep = await storage.getStep(session.currentStepId);
      if (lastStep) {
        currentContext = JSON.parse(JSON.stringify(lastStep.context));
      } else {
        currentContext = createInitialContext(t);
      }
    } else {
      currentContext = createInitialContext(t);
    }

    // Create processing chain
    const chain = createProcessingChain();

    // Get language from context
    const language = c.get('language') as string;

    // Prepare request object
    const request = { input, t, language };

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
    await sessionService.updateCurrentStep(sessionId, newStep.id);

    return c.json({
      step: newStep,
      sessionId,
    });
  } catch (error: any) {
    console.error('Error processing step:', error);
    const t = c.get('t') as I18nContext['t'];
    return c.json({ error: { code: 'INTERNAL_ERROR', message: t('common:errors.internalError', error.message) } }, 500);
  }
});

/**
 * GET /api/game/context/:sessionId - Get current context
 */
gameRouter.get('/context/:sessionId', async (c) => {
  try {
    const t = c.get('t') as I18nContext['t'];
    const sessionId = c.req.param('sessionId');
    const userId = c.get('userId') as string;

    const sessionService = getSession();
    const storage = getStepStorage();

    const session = await sessionService.getSession(sessionId);
    if (!session) {
      return c.json({ error: { code: 'SESSION_NOT_FOUND', message: t('common:errors.sessionNotFound', 'Session not found') } }, 404);
    }

    if (session.userId !== userId) {
      return c.json({ error: { code: 'FORBIDDEN', message: t('common:errors.forbidden', 'Access denied') } }, 403);
    }

    if (!session.currentStepId) {
      return c.json({ context: createInitialContext(t) });
    }

    const currentStep = await storage.getStep(session.currentStepId);
    if (!currentStep) {
      return c.json({ context: createInitialContext(t) });
    }

    return c.json({ context: currentStep.context });
  } catch (error: any) {
    console.error('Error getting context:', error);
    const t = c.get('t') as I18nContext['t'];
    return c.json({ error: { code: 'INTERNAL_ERROR', message: t('common:errors.internalError', error.message) } }, 500);
  }
});

/**
 * GET /api/game/history/:sessionId - Get step history
 */
gameRouter.get('/history/:sessionId', async (c) => {
  try {
    const t = c.get('t') as I18nContext['t'];
    const sessionId = c.req.param('sessionId');
    const userId = c.get('userId') as string;

    const sessionService = getSession();
    const storage = getStepStorage();

    const session = await sessionService.getSession(sessionId);
    if (!session) {
      return c.json({ error: { code: 'SESSION_NOT_FOUND', message: t('common:errors.sessionNotFound', 'Session not found') } }, 404);
    }

    if (session.userId !== userId) {
      return c.json({ error: { code: 'FORBIDDEN', message: t('common:errors.forbidden', 'Access denied') } }, 403);
    }

    const stepIds = await sessionService.getStepHistory(sessionId);
    const steps = await storage.getSteps(stepIds);

    return c.json({ steps });
  } catch (error: any) {
    console.error('Error getting history:', error);
    const t = c.get('t') as I18nContext['t'];
    return c.json({ error: { code: 'INTERNAL_ERROR', message: t('common:errors.internalError', error.message) } }, 500);
  }
});

/**
 * POST /api/game/rollback - Rollback to a specific step
 */
gameRouter.post('/rollback', async (c) => {
  try {
    const t = c.get('t') as I18nContext['t'];
    const body = await c.req.json<{ stepIndex: number }>();
    const { stepIndex } = body;

    if (typeof stepIndex !== 'number' || stepIndex < 0) {
      return c.json({ error: { code: 'INVALID_INPUT', message: t('common:errors.invalidStepIndex', 'Invalid step index') } }, 400);
    }

    const sessionId = c.get('sessionId') as string;
    const userId = c.get('userId') as string;
    const sessionService = getSession();
    const storage = getStepStorage();

    const session = await sessionService.getSession(sessionId);
    if (!session) {
      return c.json({ error: { code: 'SESSION_NOT_FOUND', message: t('common:errors.sessionNotFound', 'Session not found') } }, 404);
    }

    if (session.userId !== userId) {
      return c.json({ error: { code: 'FORBIDDEN', message: t('common:errors.forbidden', 'Access denied') } }, 403);
    }

    const deletedStepIds = await sessionService.rollbackToStep(sessionId, stepIndex);
    
    for (const stepId of deletedStepIds) {
      await storage.deleteStep(stepId);
    }

    const currentStep = await storage.getStep(session.stepHistory[stepIndex]);

    return c.json({
      step: currentStep,
      sessionId,
    });
  } catch (error: any) {
    console.error('Error rolling back:', error);
    const t = c.get('t') as I18nContext['t'];

    if (error.statusCode === 400) {
      return c.json({ error: { code: 'INVALID_INPUT', message: t('common:errors.invalidStepIndex', 'Invalid step index') } }, 400);
    }

    return c.json({ error: { code: 'INTERNAL_ERROR', message: t('common:errors.internalError', error.message) } }, 500);
  }
});

export default gameRouter;
