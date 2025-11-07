def _handle_link_click(self, event) -> bool:
        """Handle link clicks in the output log.
        
        Args:
            event: The click event
            
        Returns:
            True if a link was clicked and handled, False otherwise
        """
        try:
            # Get the RichLog widget
            main_log = self.query_one("#main_log", RichLog)
            
            # Convert screen coordinates to widget coordinates
            widget_x = event.screen_x - main_log.region.x
            widget_y = event.screen_y - main_log.region.y
            
            # Get the text at the click position
            # This is a simplified approach - in a real implementation,
            # you'd need to parse the RichLog content more carefully
            log_content = "\n".join(self._log_text_buffer)
            
            # Find URLs in the log content
            url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+|www\.[^\s<>"{}|\\^`\[\]]+|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            urls = re.findall(url_pattern, log_content)
            
            if urls:
                # For simplicity, open the first URL found
                # In a more sophisticated implementation, you'd determine
                # which URL was actually clicked based on position
                url = urls[0]
                
                # Add www. prefix if missing for http/https URLs
                if url.startswith('www.') and not url.startswith('http'):
                    url = 'https://' + url
                
                # Check if it's an email address
                if '@' in url and not url.startswith('mailto:'):
                    url = 'mailto:' + url
                
                try:
                    self._update_log_view(f"[bold blue]> 🌐 正在打开链接: {url}[/bold blue]")
                    
                    # Use appropriate method to open the URL
                    if url.startswith('mailto:'):
                        # Open email client
                        subprocess.run(['start', 'mailto:' + url[7:]], shell=True)
                    else:
                        # Open web browser
                        webbrowser.open(url)
                    
                    return True
                except Exception as e:
                    self._update_log_view(f"[bold red]> ❌ 无法打开链接: {e}[/bold red]")
                    return False
            
            return False
            
        except Exception as e:
            print(f"Error handling link click: {e}")
            return False

    def _update_current_model(self, model_name: str) -> None:
        """Update the current model display and status bar."""
        self._current_model = model_name
        self._model_name = model_name  # Also update the model_name for status bar
        # Update status bar to reflect model change
        current_status = "Idle" if not self._current_debate['is_active'] else "Debating"
        self._update_status_bar(current_status)

        # Log model change
        self._update_log_view(f"[bold blue]> 🔄 Model switched to {model_name}[/bold blue]")
        
        # Log model change in debates
        if self._current_debate['is_active'] and self._current_debate['current_participant']:
            self._update_log_view(f"[dim]🔄 Model switched to {model_name} for {self._current_debate['current_participant']}[/dim]")