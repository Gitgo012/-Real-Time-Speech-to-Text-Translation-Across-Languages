/**
 * Vitest setup file
 */
import "@testing-library/jest-dom";

// Mock window.matchMedia
Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Mock navigator.mediaDevices
Object.defineProperty(navigator, "mediaDevices", {
  value: {
    getUserMedia: vi.fn().mockResolvedValue({
      getTracks: () => [],
      getAudioTracks: () => [],
    }),
  },
});

// Mock AudioContext
global.AudioContext = class {
  constructor() {
    this.audioWorklet = {
      addModule: vi.fn().mockResolvedValue(undefined),
    };
    this.destination = {};
    this.currentTime = 0;
    this.sampleRate = 48000;
  }
  createMediaStreamSource() {
    return { connect: vi.fn(), disconnect: vi.fn() };
  }
  close() {}
};

global.AudioWorkletNode = class {
  constructor() {
    this.port = {
      onmessage: null,
      postMessage: vi.fn(),
    };
  }
  connect() {}
  disconnect() {}
};
