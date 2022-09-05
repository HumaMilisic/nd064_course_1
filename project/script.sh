docker build --tag=techtrends .

docker run -p 7111:3111 --name techtrends -d techtrends:latest