package authenticatedRequests

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"time"

	"github.com/Vchen7629/Cyphria/loginapi/config/redis"
	"github.com/Vchen7629/Cyphria/loginapi/internal/rediscomponents"
)

var client = redisClient.GetRedisClient()

func CheckIfSessionExistsAndNotExpired(cookie string) (bool, error) {
	found, createdAt, err := redisComponents.CheckSessionExistsRedis(cookie)

	if err != nil {
		return false, fmt.Errorf(err.Error())
	}

	// add test to check if sessionID it returns 500 error and deletes session token
	if !found {
		return false, fmt.Errorf("SessionID expired/doesnt exist")
	}

	valid, _ := redisComponents.CheckIfSessionIsOverAbsoluteExpiration(cookie, createdAt)

	if !valid && found {
		redisComponents.RemoveSessionTokenRedis(cookie)
		return false, fmt.Errorf("Session Exists but over 12 hours old")
	} else if !valid {
		return false, fmt.Errorf("z")
	}

	return true, nil
}

func FetchUserDataHandler(w http.ResponseWriter, r *http.Request) {
	tTime := time.Now()
	var (
		username 	string
		sessionErr 	error
	)

	ctime := time.Now()
	w.Header().Set("Content-Type", "Application/json")
	cookie, cookieErr := r.Cookie("accessToken")
	cookieTime := time.Since(ctime)

	if cookieErr != nil {
        http.Error(w, "Unauthorized", http.StatusUnauthorized)
        return
    }

	sessionCookie := cookie.Value

	sessionValid, checkErr := CheckIfSessionExistsAndNotExpired(sessionCookie)

	if checkErr != nil {
		cookie := &http.Cookie{
			Name: 	"accessToken",
			Value: 	"",
			MaxAge: -1,
			Path: 	"/",
		}
	
		http.SetCookie(w, cookie)

		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(map[string]string{
			"message": checkErr.Error(),
		})
		return
	}

	if !sessionValid {
		cookie := &http.Cookie{
			Name: 	"accessToken",
			Value: 	"",
			MaxAge: -1,
			Path: 	"/",
		}
	
		http.SetCookie(w, cookie)

		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(map[string]string{
			"message": "Session Invalid, Login again",
		})
		return
	}

	ftime := time.Now()
	username, sessionErr = redisComponents.FetchSessionDataRedis(cookie.Value)
	findTime := time.Since(ftime)

	if sessionErr != nil {
		cookie := &http.Cookie{
			Name: 	"accessToken",
			Value: 	"",
			MaxAge: -1,
			Path: 	"/",
		}
	
		http.SetCookie(w, cookie)
		
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(map[string]string{
			"message": sessionErr.Error(),
		})
		return
	}

	wtime := time.Now()
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]string{
		"username": username,
	})
	writeTime := time.Since(wtime)
	totalTime := time.Since(tTime)

	log.Printf("Login timing - cookieParseTime: %v, fetch key time: %v, write time: %v, Total: %v",
		cookieTime, findTime, writeTime, totalTime)
}