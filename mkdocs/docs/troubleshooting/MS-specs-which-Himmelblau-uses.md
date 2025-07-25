This page is intended as a place to gather all the MS specification documents that Himmelblau implements, as well as comments about the accuracy of the specs.

* [[MS-OAPX]](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-oapx): OAuth 2.0 Protocol Extensions
  * Used in the MSAL PublicClientApplication for general authentication.
* [[MS-OAPXBC]](https://learn.microsoft.com/en-us/openspecs/windows_protocols/MS-OAPXBC): OAuth 2.0 Protocol Extensions for Broker Clients
  * Used in the MSAL BrokerClientApplication for PRT requests.
* [[MS-DVRJ]](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-dvrj): Device Registration Join Protocol
  * Sections 3.1.5.1.1.1 and 3.1.5.1.1.2 are mostly accurate and used in [[MS-DRS] Section 2.1](https://github.com/himmelblau-idm/aad-join-spec/blob/main/aad-join-spec.md#21-join-service-details).
* [[MS-DVRE]](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-dvre): Device Registration Enrollment Protocol
  * This protocol appears to be used by the DRS service in Azure to enroll the client device. Section 2.3.3 Alt-Security-Identities matches the device object which is created within the directory. The client does not use this protocol, but is useful as a reference.
* [[MS-DVRD]](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-dvrd): Device Registration Discovery Protocol
  * Accurate, but missing many services, see [[MS-DRS] Section 3.1](https://github.com/himmelblau-idm/aad-join-spec/blob/main/aad-join-spec.md#31-device-registration-discovery-service).
* [[MS-KPP]](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-kpp): Key Provisioning Protocol
  * This is used by MSAL to provision a Windows Hello for Business key. The process for requesting a PRT using that key does not appear to be document (although MSAL copies Windows behavior here to request the PRT).