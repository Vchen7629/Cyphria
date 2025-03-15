import { createSlice } from "@reduxjs/toolkit";
import { email, userId, username } from "./types.ts";


const authSlice = createSlice({
    name: "auth",
    initialState: { userId: null, email: null, username: null, loggingOut: false }, 
    reducers: {
        setCredentials: (state, action) => {
            const { userId, email, username } = action.payload
            state.userId = userId
            state.username = username
            state.email = email
            state.loggingOut = false;
        },

        logOut: (state) => {
            state.userId = null
            state.username = null
            state.email = null
            state.loggingOut = true;
        },

        resetLoggingOutState: (state) => {
            state.loggingOut = false; 
        }
    }
})

export const { setCredentials, logOut, resetLoggingOutState } = authSlice.actions

export default authSlice.reducer

export const selectCurrentuserId = (state: userId) => state.auth.userId
export const selectCurrentEmail = (state: email) => state.auth.email;
export const selectCurrentUsername = (state: username) => state.auth.username;
export const selectLoggingOut = (state: { auth: { loggingOut: boolean }}) => state.auth.loggingOut;


