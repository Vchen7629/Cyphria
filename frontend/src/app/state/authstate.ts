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
            const { uuid, username } = action.payload
            state.userId = uuid
            state.username = username
            state.loginStatus = true;
        },

        logOut: (state) => {
            state.userId = null
            state.username = null
            state.loginStatus = false;
        },

        resetLoggingOutState: (state) => {
            state.loginStatus = false; 
        }
    }
})

export const { setCredentials, logOut, resetLoggingOutState } = authSlice.actions

export default authSlice.reducer

export const selectCurrentUserId = (state: userId) => state.auth.userId
export const selectCurrentUsername = (state: username) => state.auth.username;
export const selectLoginStatus = (state: { auth: { loginStatus: boolean }}) => state.auth.loginStatus;


