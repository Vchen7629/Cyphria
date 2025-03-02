package main

import (
	"fmt"
	"log"
	"net/http"
	"github.com/gorilla/mux"
	"github.com/joho/godotenv"
	"github.com/vchen7629/cyphria/login-api/config/db_config"
	"github.com/vchen7629/cyphria/login-api/internal/db_connection"
	"github.com/vchen7629/cyphria/login-api/internal/login"
	"github.com/vchen7629/cyphria/login-api/internal/logout"
	"github.com/vchen7629/cyphria/login-api/internal/signup"
)


func LoadEnvFile() {
	err := godotenv.Load("../../.env")
	if err != nil {
		log.Fatal("Error loading .env file\n")
	}	
}

func main(){
	r := mux.NewRouter()
	r.HandleFunc("/", helloWorld)
	r.HandleFunc("/login", login.Login)
	r.HandleFunc("/logout", logout.Logout)
	r.HandleFunc("/signup",  signup.CreateNewUser)
	http.Handle("/", r)
	LoadEnvFile()
	dbconfig.Config()
	dbconn.Main()
	srv := &http.Server {
		Handler: r,
		Addr: "127.0.0.1:3000",
	}

	log.Fatal(srv.ListenAndServe())
}

func helloWorld(w http.ResponseWriter, r *http.Request) {
	fmt.Printf("Hello from golang api!\n")
}