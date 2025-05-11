package accountComponents

import (
	"encoding/json"
	"fmt"
	"net/http"
	"github.com/Vchen7629/Cyphria/loginapi/internal/rediscomponents"
)

func RedisHandler(sessionIDCookie string) (bool, error) {
	sessionErr := redisComponents.RemoveSessionTokenRedis(sessionIDCookie)

	if sessionErr != nil {
		return false, fmt.Errorf(sessionErr.Error())
	}
	
	return true, nil
}

func LogoutHandler(w http.ResponseWriter, r *http.Request) {
	sessionIDCookie, cookieErr := r.Cookie("accessToken")
	sessionID := sessionIDCookie.Value
	w.Header().Set("Content-Type","application/json")

	if cookieErr != nil {
        http.Error(w, "Unauthorized", http.StatusUnauthorized)
        return
    }

	successRedis, redisErr := RedisHandler(sessionID)

	if successRedis {
		cookie := &http.Cookie{
			Name: 	"accessToken",
			Value: 	"",
			MaxAge: -1,
			Path: 	"/",
		}
	
		http.SetCookie(w, cookie)
	
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(map[string]string{"message": "Successfully Logged Out!"})
	} else {
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]string{
			"message": redisErr.Error(),
		})
	}
}