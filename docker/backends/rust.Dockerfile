FROM rust:1.72-slim
WORKDIR /work
COPY compile_rust.sh /usr/local/bin/compile_rust.sh
RUN chmod +x /usr/local/bin/compile_rust.sh
CMD ["/usr/local/bin/compile_rust.sh"]
