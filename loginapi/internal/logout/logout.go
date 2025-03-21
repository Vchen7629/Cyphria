package logout

import (
	"encoding/json"
	"net/http"
)

func Logout(w http.ResponseWriter, r *http.Request) {
	cookie := &http.Cookie{
		Name: 	"accessToken",
		Value: 	"",
		MaxAge: -1,
		Path: 	"/",
	}

	http.SetCookie(w, cookie)

	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]string{"message": "Successfully Logged Out!"})
}