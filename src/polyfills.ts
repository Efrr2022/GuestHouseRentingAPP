
// For Angular+ does not include shims for 'global' or 'process' as provided in previous version
(window as any).global = window;
(window as any).process = {
    env: { DEBUG: undefined },
};
