export interface ScenarioStep {
  id: string;
  name: string;
  icon: string;
  status: 'pending' | 'running' | 'success' | 'error';
  description: string;
}

export interface Scenario {
  id: string;
  name: string;
  description: string;
  steps: ScenarioStep[];
}

export const mockScenarios: Scenario[] = [
  {
    id: 'order-creation',
    name: 'Order Creation Flow',
    description: 'Complete order creation and payment flow',
    steps: [
      {
        id: 'step-1',
        name: 'Send HTTP /orders',
        icon: 'Send',
        status: 'success',
        description: 'POST request to create order'
      },
      {
        id: 'step-2',
        name: 'Expect DB Insert',
        icon: 'Database',
        status: 'success',
        description: 'Verify order stored in database'
      },
      {
        id: 'step-3',
        name: 'Emit OrderCreated',
        icon: 'MessageSquare',
        status: 'success',
        description: 'Publish domain event'
      },
      {
        id: 'step-4',
        name: 'Trigger Scheduler',
        icon: 'Clock',
        status: 'running',
        description: 'Schedule payment check'
      },
      {
        id: 'step-5',
        name: 'Call Payment Mock',
        icon: 'CreditCard',
        status: 'pending',
        description: 'Process payment request'
      },
      {
        id: 'step-6',
        name: 'Verify Final Status',
        icon: 'CheckCircle',
        status: 'pending',
        description: 'Confirm order completion'
      }
    ]
  },
  {
    id: 'payment-processing',
    name: 'Payment Processing Flow',
    description: 'Test payment gateway integration',
    steps: [
      {
        id: 'step-1',
        name: 'Receive Payment Request',
        icon: 'Inbox',
        status: 'pending',
        description: 'Accept payment request'
      },
      {
        id: 'step-2',
        name: 'Validate Payment',
        icon: 'Shield',
        status: 'pending',
        description: 'Validate payment data'
      },
      {
        id: 'step-3',
        name: 'Call Payment Gateway',
        icon: 'ExternalLink',
        status: 'pending',
        description: 'External API call'
      },
      {
        id: 'step-4',
        name: 'Update Order Status',
        icon: 'Edit',
        status: 'pending',
        description: 'Update order in DB'
      },
      {
        id: 'step-5',
        name: 'Emit Payment Event',
        icon: 'MessageSquare',
        status: 'pending',
        description: 'Publish payment event'
      },
      {
        id: 'step-6',
        name: 'Send Confirmation',
        icon: 'Mail',
        status: 'pending',
        description: 'Send confirmation message'
      }
    ]
  }
];

