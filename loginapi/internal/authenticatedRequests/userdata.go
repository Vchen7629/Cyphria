package authenticatedRequests

import (
	"net/http"
	"encoding/json"
	"github.com/Vchen7629/Cyphria/loginapi/config/redis"
	"github.com/Vchen7629/Cyphria/loginapi/internal/components"

)

var client = redisClient.GetRedisClient()

func FetchUserDataHandler(w http.ResponseWriter, r *http.Request) {
	var (
		username 	string
		sessionErr 	error
		
	)
	cookie, cookieErr := r.Cookie("accessToken")

	if cookieErr != nil {
        http.Error(w, "Unauthorized", http.StatusUnauthorized)
        return
    }

	sessionToken := cookie.Value

	if sessionToken == "" {
		http.Error(w, "No Session Token Found/Returned", http.StatusNotFound)
		return
	}

	found, err := components.CheckSessionExistsRedis(cookie.Value)

	if err == nil && found {
		username, sessionErr = components.FetchSessionDataRedis(cookie.Value)
	} else {
		w.WriteHeader(http.StatusNotFound)
		json.NewEncoder(w).Encode(map[string]string{
			"message": "SessionID Doesnt exist in Redis",
		})
		return
	}

	w.Header().Set("Content-Type", "Application/json")

	if sessionErr != nil {
		w.WriteHeader(http.StatusNotFound)
		json.NewEncoder(w).Encode(map[string]string{
			"message": sessionErr.Error(),
		})
	}  else {
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(map[string]string{
			"username": username,
		})
	}
}