import { configureStore } from "@reduxjs/toolkit";
import { setupListeners } from "@reduxjs/toolkit/query";
import uiReducer from './state/ui';
import { querySlice } from "./base/insightsSlice";

export const store = configureStore({
    reducer: {
        [querySlice.reducerPath]: querySlice.reducer,
        ui: uiReducer,
    },
    middleware: getDefaultMiddleware => getDefaultMiddleware()
        .concat(querySlice.middleware),
    devTools: true
})

setupListeners(store.dispatch)