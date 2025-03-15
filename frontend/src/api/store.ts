import { configureStore } from "@reduxjs/toolkit";
import { baseSlice } from "./base/baseSlice";
import { setupListeners } from "@reduxjs/toolkit/query";
import authReducer from "./state/authstate"

export const store = configureStore({
    reducer: {
        [baseSlice.reducerPath]: baseSlice.reducer,
        auth: authReducer,
    },
    middleware: getDefaultMiddleware => getDefaultMiddleware()
        .concat(baseSlice.middleware),
    devTools: true
})

setupListeners(store.dispatch)