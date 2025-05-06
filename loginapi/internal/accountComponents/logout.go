package accountComponents

import (
	"fmt"
	"net/http"
	"encoding/json"
	"github.com/Vchen7629/Cyphria/loginapi/internal/components"
)

type LogoutCredentials struct {
	UUID string `json:"uuid"`
}

func RedisHandler(sessionIDCookie string) (bool, error) {
	exists, sessionErr := components.CheckSessionExistsRedis(sessionIDCookie)

	if sessionErr != nil {
		return false, fmt.Errorf(sessionErr.Error())
	}

	if exists {
		sessionErr := components.RemoveSessionTokenRedis(sessionIDCookie)

		if sessionErr != nil {
			return false, fmt.Errorf(sessionErr.Error())
		}
	}

	return true, nil
}

func PostgresHandler(UUID string) (bool, error) {
	err := components.RemoveSessionTokenPostgres(UUID)

	if err != nil {
		return false, err
	}

	return true, nil
}

func LogoutHandler(w http.ResponseWriter, r *http.Request) {
	var payload LogoutCredentials
	sessionIDCookie, cookieErr := r.Cookie("accessToken")
	sessionID := sessionIDCookie.Value
	w.Header().Set("Content-Type","application/json")

	requestbodyerr := json.NewDecoder(r.Body).Decode(&payload)
	if requestbodyerr != nil {
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]string{
			"message": "error parsing json body",
		})
	}
	uuid := payload.UUID

	if cookieErr != nil {
        http.Error(w, "Unauthorized", http.StatusUnauthorized)
        return
    }

	if requestbodyerr != nil {
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]string{
			"message": "error parsing json body",
		})
	}

	successRedis, redisErr := RedisHandler(sessionID)

	successPostgres, postgresErr := PostgresHandler(uuid)

	if successRedis && successPostgres {
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
		if postgresErr.Error() == "No uuid provided" {
			w.WriteHeader(http.StatusBadRequest)
			json.NewEncoder(w).Encode(map[string]string{"message": "Logout Failed, Missing UUID"})
		} else if postgresErr.Error() == "Internal Error" {
			w.WriteHeader(http.StatusInternalServerError)
			json.NewEncoder(w).Encode(map[string]string{"message": postgresErr.Error()})
		} else if postgresErr.Error() == "No rows were updated" {
			w.WriteHeader(http.StatusBadRequest)
			json.NewEncoder(w).Encode(map[string]string{"message": postgresErr.Error()})
		} else {
			w.WriteHeader(http.StatusBadRequest)
			json.NewEncoder(w).Encode(map[string]string{"message": redisErr.Error()})
		}
	}
}