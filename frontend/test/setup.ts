import { vi } from "vitest";

vi.mock('../src/api/client/basePath', () => ({
    insights_api: {
        get: vi.fn()
    }
}))