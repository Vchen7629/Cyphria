# Cyphria
<h2>Introduction</h2>
<p>
  This project aims to implement an web application that allows Users to draw insights from Reddit Posts. 
  Users should be able to filter by topics/categories/subreddits to view trends and Sentiments torward the topic/category/subreddit.
</p>
<h2>Motivation</h2>
<p>
  Since Reddit is my most frequently used social media application, i thought it would be cool to build an project that allows me to view insights from a large portion of reddit that
  isn't possible from just searching up topics. I also wanted to learn about distributed systems and various open source software. These motivation combined led me to 
  start working on this project. 
</p>
<h2>Architecture</h2>
<img src="architecture_2.0.svg" alt="Architecture image" />
<h2>Key Technologies Used</h2>
<h3>Frontend</h3>
<ul>
  <li>React: I chose React as my main frontend technology since I'm enjoy working with React</li>
  <li>TailwindCSS: I chose tailwind CSS since </li>
</ul>

<h3>Data Processing</h3>
<ul>
  <li>Apache Spark: </li>
  <li>Apache Kafka: </li>
</ul>

<h3>Database</h3>
<ul>
  <li>Milvus: Milvus is the vector database used to store the various social media post vector embeddings</li>
  <li>Postgres: Postgres is used to store the user account data for the application</li>
  <li>Redis: Redis is used in my system to handle caching, reducing the load on my database and decreasing latency</li>
</ul>

<h3>Metrics/logging</h3>
<ul>
  <li>Grafana: I'm using my grafana cluster Verturus to aggregate and display my metrics and logs from various services in the application for ease of view</li>
  <li>Prometheus: Prometheus is used in my application to collect metrics from my various services and send it to my grafana cluster</li>
  <li>Grafana Loki: Loki is used in my application to collect logs and send it to my grafana cluster</li>
</ul>

<h2>Getting Started</h2>
