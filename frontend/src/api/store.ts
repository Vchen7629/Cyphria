import { configureStore } from "@reduxjs/toolkit";
import { authSlice } from "./base/authSlice";
import { setupListeners } from "@reduxjs/toolkit/query";
import authReducer from "./state/authstate"
import { querySlice } from "./base/querySlice";

export const store = configureStore({
    reducer: {
        [authSlice.reducerPath]: authSlice.reducer,
        [querySlice.reducerPath]: querySlice.reducer,
        auth: authReducer,
    },
    middleware: getDefaultMiddleware => getDefaultMiddleware()
        .concat(authSlice.middleware)
        .concat(querySlice.middleware),
    devTools: true
})

setupListeners(store.dispatch)