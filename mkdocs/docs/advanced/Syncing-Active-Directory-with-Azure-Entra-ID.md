#### **3. Install and Configure Microsoft Entra Connect**
1. Download **Microsoft Entra Connect** from Microsoft:  
   [https://www.microsoft.com/en-us/download/details.aspx?id=47594](https://www.microsoft.com/en-us/download/details.aspx?id=47594)
2. Run the installer on your AD domain controller or another dedicated server.
3. Choose **"Custom installation"** (recommended for better control).
4. **Connect to Azure Entra ID** using **Global Admin credentials**.
5. **Connect to Active Directory**:
   - Enter your **AD DS credentials** (Enterprise Admin).
   - It should verify and list your domain.
6. **Choose Sync Options**:
   - If you want password hash synchronization (PHS), select it.
   - If using Pass-through Authentication (PTA) or Federation, configure as needed.
7. **Select "Start Synchronization"** and finish setup.