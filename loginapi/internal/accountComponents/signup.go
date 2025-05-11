package accountComponents

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"time"

	dbconn "github.com/Vchen7629/Cyphria/loginapi/config/postgres"
	"github.com/Vchen7629/Cyphria/loginapi/internal/components"
	"github.com/Vchen7629/Cyphria/loginapi/internal/rediscomponents"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgconn"
	"golang.org/x/crypto/bcrypt"
)

type SignUpUserRequest struct {
	Username string `json:"username"`
	Password string `json:"password"`
}

func HashPassword(password string) (string, error) {
	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(password), 11);
	if err != nil {
		return "", err
	}

	return string(hashedPassword), nil
}

func CreateNewUser(username, password string) (bool, string, error) {
	var inserted bool

	if username == "" {
		return false, "", fmt.Errorf("Missing Username, please provide an username")
	} else if password == "" {
		return false, "", fmt.Errorf("Missing Password, please provide an password")
	}

	sessionID, sessionErr, sessionSuccess := components.GenerateSessionToken()
	uuid := uuid.New()

	redisErr := redisComponents.CreateRedisSessionID(sessionID, username, uuid.String())

	if sessionErr != nil {
		return false, "", fmt.Errorf("Error Generating Random Token")
	}
	
	if sessionSuccess && redisErr == nil {
		err := dbconn.DBConn.QueryRow(context.Background(), `
			INSERT INTO useraccount (uuid, username, password, creation)
			VALUES (
				$1,
				$2,
				$3,
				$4
			) 
			RETURNING true;
		`, uuid, username, password, time.Now()).Scan(&inserted)

		if err == pgx.ErrNoRows {
			return false, "", nil
		}

		if err != nil {
			var pgErr *pgconn.PgError
			if errors.As(err, &pgErr) {
				if pgErr.Code == "23505" {
					return false, "", fmt.Errorf("Username already Exists")
				}
			} else {
				return true, "", fmt.Errorf("error creating a new user: %s", pgErr.Message)
			}
		}
	} else {
		return false, "", fmt.Errorf("error")
	}
	
	return true, sessionID, nil
}

func SignUpHandler(w http.ResponseWriter, r *http.Request) {
	var payload SignUpUserRequest
	bodyerr := json.NewDecoder(r.Body).Decode(&payload)
	if bodyerr != nil {
		http.Error(w, "Error parsing json", http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	hashed, hasherror := HashPassword(payload.Password)
	if hasherror != nil {
		http.Error(w, fmt.Sprintf("Error hashing password: %v", hasherror), http.StatusInternalServerError)
		return
	}

	_, sessionID, err := CreateNewUser(payload.Username, hashed)

	if err != nil {
		w.Header().Set("Content-Type","application/json")
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(map[string]string{
			"message": err.Error(),
		})
		return
	}

	cookie := http.Cookie{
		Name: 		"accessToken",
		Value: 		sessionID,
		Expires: 	time.Now().Add(12 * time.Hour),
		Path: 		"/",
		Secure:     true,
		HttpOnly:   true,
		SameSite:   http.SameSiteLaxMode,
	}

	http.SetCookie(w, &cookie)

	response := map[string]string{
		"message": "user created Successfully!",
	}

	w.Header().Set("Content-Type","application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(response)
}