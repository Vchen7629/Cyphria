import { createSlice } from "@reduxjs/toolkit";
import { userId, username } from "./types.ts";
import { getUserDataFromToken } from "../../utils/tokenUtils.ts";


const tokenData = getUserDataFromToken()

const authSlice = createSlice({
    name: "auth",
    initialState: { 
        userId: tokenData?.userId || null, 
        username: tokenData?.username || null, 
        loginStatus: false 
    }, 
    reducers: {
        setCredentials: (state, action) => {
            const { userId, username } = action.payload
            state.userId = userId
            state.username = username
            state.loginStatus = false;
        },

        logOut: (state) => {
            state.userId = null
            state.username = null
            state.loginStatus = true;
        },

        resetLoggingOutState: (state) => {
            state.loginStatus = false; 
        }
    }
})

export const { setCredentials, logOut, resetLoggingOutState } = authSlice.actions

export default authSlice.reducer

export const selectCurrentuserId = (state: userId) => state.auth.userId
export const selectCurrentUsername = (state: username) => state.auth.username;
export const selectLoginStatus = (state: { auth: { loginStatus: boolean }}) => state.auth.loginStatus;


