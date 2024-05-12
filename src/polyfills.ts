import 'core-js/es/typed-array';
import 'core-js/es/object';
(window as any).global = window;
(window as any).process = {
  env: { DEBUG: undefined },
};

