package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
    "syscall"
	"context"
	"github.com/gorilla/mux"
	"github.com/joho/godotenv"
	"github.com/Vchen7629/Cyphria/loginapi/config/middleware"
	"github.com/Vchen7629/Cyphria/loginapi/config/poolconfig"
	dbconn "github.com/Vchen7629/Cyphria/loginapi/config/postgres"
	"github.com/Vchen7629/Cyphria/loginapi/config/redis"
	"github.com/Vchen7629/Cyphria/loginapi/internal/login"
	"github.com/Vchen7629/Cyphria/loginapi/internal/logout"
	"github.com/Vchen7629/Cyphria/loginapi/internal/signup"
	"github.com/Vchen7629/Cyphria/loginapi/internal/authenticatedRequests"
)


func LoadEnvFile() {
	err := godotenv.Load(".env")
	if err != nil {
		log.Fatal("Error loading .env file\n")
	}	
}

func RouteHandlers(r *mux.Router) {
	r.HandleFunc("/", helloWorld)
	r.HandleFunc("/login", login.LoginHandler).Methods(http.MethodPost, http.MethodOptions)
	r.HandleFunc("/logout", logout.Logout).Methods(http.MethodPost, http.MethodOptions)
	r.HandleFunc("/signup",  signup.HttpHandler).Methods(http.MethodPost, http.MethodOptions)
	r.HandleFunc("/getuserdata", authenticatedRequests.FetchUserDataHandler).Methods(http.MethodPost, http.MethodOptions)
	http.Handle("/", r)
}

func main(){
	r := mux.NewRouter()
	LoadEnvFile()
	config.PoolConfig()
	dbconn.Main()
	redisClient.GetRedisClient()
	RouteHandlers(r)
	
	corsRouter := middleware.CorsMiddleware(r)
	srv := &http.Server {
		Handler: corsRouter,
		Addr: "0.0.0.0:3000",
	}
	
	// go channel to listen for os quit command
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, os.Interrupt, syscall.SIGTERM)

	go func() {
		<-quit 
		log.Println("Shutting down Server")

		err := srv.Shutdown(context.Background())

		if err != nil {
			log.Fatalf("Error Shutting Down Server: %s", err)
		}

		dbconn.DBConn.Close()
	}()

	err := srv.ListenAndServe() 
	
	if err != nil && err != http.ErrServerClosed {
		log.Fatalf("ListenAndServe(): %s", err)
	}
}

func helloWorld(w http.ResponseWriter, r *http.Request) {
	fmt.Printf("Hello from golang api!\n")
}