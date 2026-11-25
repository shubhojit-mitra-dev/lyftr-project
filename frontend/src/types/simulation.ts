export type FailureSimulationPreset =
  | 'none'
  | 'key_1=429'
  | 'key_1=429,key_2=500'
  | '*=429'
  | 'custom';
