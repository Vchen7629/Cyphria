package signup

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"time"
	"errors"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgconn"
	dbconn "github.com/Vchen7629/Cyphria/loginapi/config/postgres"
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

func CreateNewUser(username, password string) (bool, error) {
	var inserted bool

	if username == "" {
		return false, fmt.Errorf("Missing Username, please provide an username")
	} else if password == "" {
		return false, fmt.Errorf("Missing Password, please provide an password")
	}
	
	err := dbconn.DBConn.QueryRow(context.Background(), `
		INSERT INTO useraccount (uuid, username, password, creation)
		VALUES (
			$1,
			$2,
			$3,
			$4
		) 
		RETURNING true;
	`, uuid.New(), username, password, time.Now()).Scan(&inserted)

	if err == pgx.ErrNoRows {
		return false, nil
	}

	if err != nil {
		var pgErr *pgconn.PgError
		if errors.As(err, &pgErr) {
			if pgErr.Code == "23505" {
				return false, fmt.Errorf("Username already Exists")
			}
		} else {
			return true, fmt.Errorf("error creating a new user: %w", pgErr.Message)
		}
	}
	
	return true, nil
}

func HttpHandler(w http.ResponseWriter, r *http.Request) {
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

	_, err := CreateNewUser(payload.Username, hashed)

	if err != nil {
		w.Header().Set("Content-Type","application/json")
		if err.Error() == "Username already Exists" {
			w.WriteHeader(http.StatusConflict)
			json.NewEncoder(w).Encode(map[string]string{
				"message": "Username Already Exists, Try Again!",
			})
			return
		} else if err.Error() == "Missing Username, please provide an username" {
			w.WriteHeader(http.StatusBadRequest)
			json.NewEncoder(w).Encode(map[string]string{
				"message": err.Error(),
			})
			return
		} else if err.Error() == "Missing Password, please provide an password" {
			w.WriteHeader(http.StatusBadRequest)
			json.NewEncoder(w).Encode(map[string]string{
				"message": err.Error(),
			})
			return
		} else {
			w.WriteHeader(http.StatusInternalServerError)
			json.NewEncoder(w).Encode(map[string]string{
				"message": err.Error(),
			})
			return
		}
	}

	response := map[string]string{
		"message": "user created Successfully!",
	}

	w.Header().Set("Content-Type","application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(response)
}