# Use PHP 8.2 CLI as base
FROM php:8.2-cli

# Set working directory inside container
WORKDIR /app

# Install system dependencies and PHP MongoDB extension
RUN apt-get update && apt-get install -y \
    git unzip libssl-dev libcurl4-openssl-dev pkg-config libssl-dev \
    && docker-php-ext-install pcntl \
    && pecl install mongodb \
    && docker-php-ext-enable mongodb

# Copy Composer from official Composer image
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

# Copy project files into the container
COPY . .

# Install PHP dependencies if composer.json exists
RUN if [ -f "composer.json" ]; then composer install --no-dev --optimize-autoloader --ignore-platform-req=ext-mongodb; fi

# Expose port for internal web server
EXPOSE 5001

# Start built-in PHP server
CMD ["php", "-S", "0.0.0.0:5001", "index.php"]